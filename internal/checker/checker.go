package checker

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/json"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/user/hunter/internal/models"
)

var httpClient *http.Client

func init() {
	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     30 * time.Second,
		TLSClientConfig:     &tls.Config{InsecureSkipVerify: true},
	}
	httpClient = &http.Client{
		Transport: transport,
		Timeout:   60 * time.Second,
	}
}

var defaultUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

var wafFingerprints = []string{
	".loading-spinner{visibility:hidden}body.no-js .challenge-running",
	"AwsWafIntegration.forceRefreshToken",
	"perimeterxIdentifiers",
	"cf-challenge-running",
}

func CheckSite(ctx context.Context, site models.Site, username string, timeout time.Duration) models.Result {
	result := models.Result{
		Site:     site.Name,
		URLMain:  site.URLMain,
		Username: username,
		Country:  site.Countries,
		Category: site.Category,
	}

	effective, status := effectiveUsername(site, username)
	if status != "" {
		result.Status = status
		return result
	}

	url := interpolate(site.URL, effective)
	result.URL = url

	probeURL := url
	if site.URLProbe != "" {
		probeURL = interpolate(site.URLProbe, effective)
	}

	method := resolveMethod(site)

	var reqBody io.Reader
	if len(site.RequestPayload) > 0 {
		b, err := interpolateRequestPayload(site.RequestPayload, effective)
		if err != nil {
			result.Status = models.StatusError
			result.Error = err.Error()
			return result
		}
		reqBody = bytes.NewReader(b)
	} else if site.RequestBody != "" {
		reqBody = strings.NewReader(strings.ReplaceAll(site.RequestBody, "{}", effective))
	}

	req, err := http.NewRequestWithContext(ctx, method, probeURL, reqBody)
	if err != nil {
		result.Status = models.StatusError
		result.Error = err.Error()
		return result
	}

	req.Header.Set("User-Agent", defaultUserAgent)
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7")
	req.Header.Set("Accept-Language", "en-US,en;q=0.9")

	if len(site.RequestPayload) > 0 {
		req.Header.Set("Content-Type", "application/json")
	} else if site.RequestBody != "" {
		hasCT := false
		for k := range site.Headers {
			if strings.EqualFold(k, "Content-Type") {
				hasCT = true
				break
			}
		}
		if !hasCT {
			req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		}
	}

	for k, v := range site.Headers {
		req.Header.Set(k, v)
	}

	client := httpClient
	if site.ErrorType == models.ErrorTypeResponseURL {
		client = &http.Client{
			Transport: httpClient.Transport,
			Timeout:   timeout,
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		}
	}

	start := time.Now()
	resp, err := client.Do(req)
	result.ResponseTime = time.Since(start).Seconds()

	if err != nil {
		result.Status = models.StatusError
		result.Error = err.Error()
		return result
	}
	defer resp.Body.Close()

	result.HTTPStatus = resp.StatusCode

	bodyBytes, _ := io.ReadAll(io.LimitReader(resp.Body, 250*1024))
	body := string(bodyBytes)

	// Instagram web_profile_info returns JSON — класифицируем по data.user, а не только по HTTP
	if site.Name == "Instagram" && strings.Contains(site.URLProbe, "web_profile_info") {
		if st, ok := instagramAPIResult(body, resp.StatusCode); ok {
			result.Status = st
			return result
		}
	}

	if site.Name == "Telegram" || strings.Contains(strings.ToLower(site.URL), "//t.me/") {
		if telegramLooksLikePublicProfile(body) {
			result.Status = models.StatusFound
		} else {
			result.Status = models.StatusNotFound
		}
		return result
	}

	for _, fp := range wafFingerprints {
		if strings.Contains(body, fp) {
			result.Status = models.StatusWAF
			return result
		}
	}

	switch site.ErrorType {
	case models.ErrorTypeStatusCode:
		if site.ExpectedHTTP > 0 {
			if resp.StatusCode == site.ExpectedHTTP {
				result.Status = models.StatusFound
			} else {
				result.Status = models.StatusNotFound
			}
			break
		}
		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			result.Status = models.StatusFound
		} else {
			result.Status = models.StatusNotFound
		}

	case models.ErrorTypeMessage:
		if site.NotFoundHTTP > 0 && resp.StatusCode == site.NotFoundHTTP {
			result.Status = models.StatusNotFound
			break
		}
		if site.ExpectedHTTP > 0 && resp.StatusCode != site.ExpectedHTTP {
			result.Status = models.StatusNotFound
			break
		}
		for _, msg := range site.ErrorMsg {
			if msg != "" && strings.Contains(body, msg) {
				result.Status = models.StatusNotFound
				break
			}
		}
		if result.Status == models.StatusNotFound {
			break
		}
		if site.FoundSubstring != "" && !strings.Contains(body, site.FoundSubstring) {
			result.Status = models.StatusNotFound
			break
		}
		result.Status = models.StatusFound

	case models.ErrorTypeResponseURL:
		if site.ErrorURL != "" {
			location := resp.Header.Get("Location")
			if strings.Contains(location, site.ErrorURL) || resp.StatusCode >= 300 {
				result.Status = models.StatusNotFound
			} else {
				result.Status = models.StatusFound
			}
		} else {
			if resp.StatusCode >= 200 && resp.StatusCode < 300 {
				result.Status = models.StatusFound
			} else {
				result.Status = models.StatusNotFound
			}
		}

	default:
		result.Status = models.StatusUnknown
	}

	return result
}

// instagramAPIResult разбирает JSON Instagram API (не полагаться только на 200 — бывает fail в теле).
func instagramAPIResult(body string, httpStatus int) (models.QueryStatus, bool) {
	body = strings.TrimSpace(body)
	if !strings.HasPrefix(body, "{") {
		return "", false
	}
	var root struct {
		Status  string          `json:"status"`
		Message string          `json:"message"`
		Data    json.RawMessage `json:"data"`
	}
	if err := json.Unmarshal([]byte(body), &root); err != nil {
		return "", false
	}
	if root.Status == "fail" {
		return models.StatusNotFound, true
	}
	msgLow := strings.ToLower(root.Message)
	if strings.Contains(msgLow, "not found") || strings.Contains(msgLow, "doesn't exist") ||
		strings.Contains(msgLow, "login_required") || strings.Contains(msgLow, "checkpoint") {
		return models.StatusNotFound, true
	}
	var dataObj struct {
		User json.RawMessage `json:"user"`
	}
	if len(root.Data) > 0 {
		_ = json.Unmarshal(root.Data, &dataObj)
		u := strings.TrimSpace(string(dataObj.User))
		if u == "" || u == "null" {
			return models.StatusNotFound, true
		}
		if strings.HasPrefix(u, "{") {
			return models.StatusFound, true
		}
	}
	if httpStatus >= 400 {
		return models.StatusNotFound, true
	}
	if httpStatus >= 200 && httpStatus < 300 {
		return models.StatusFound, true
	}
	return models.StatusNotFound, true
}

func telegramLooksLikePublicProfile(body string) bool {
	if strings.Contains(body, "tgme_page_photo") {
		return true
	}
	if strings.Contains(body, "tgme_page_context_link_wrap") {
		return true
	}
	if strings.Contains(body, "tgme_page_counter") {
		return true
	}
	if strings.Contains(body, "tgme_widget_message_user") {
		return true
	}
	if strings.Contains(body, `class="tgme_page_title"`) && strings.Contains(body, "subscriber") {
		return true
	}
	return false
}

func interpolateRequestPayload(raw json.RawMessage, username string) ([]byte, error) {
	var data interface{}
	if err := json.Unmarshal(raw, &data); err != nil {
		return nil, err
	}
	data = replaceUsernamePlaceholder(data, username)
	return json.Marshal(data)
}

func replaceUsernamePlaceholder(v interface{}, username string) interface{} {
	switch x := v.(type) {
	case map[string]interface{}:
		for k, val := range x {
			x[k] = replaceUsernamePlaceholder(val, username)
		}
		return x
	case []interface{}:
		for i, val := range x {
			x[i] = replaceUsernamePlaceholder(val, username)
		}
		return x
	case string:
		if x == "{}" {
			return username
		}
		return x
	default:
		return v
	}
}

func effectiveUsername(site models.Site, username string) (string, models.QueryStatus) {
	if !strings.Contains(username, "_") {
		if site.RegexCheck != "" {
			ok, err := regexp.MatchString(site.RegexCheck, username)
			if err != nil || !ok {
				return "", models.StatusIllegal
			}
		}
		return username, ""
	}

	if site.UnderscoreAs != "" {
		e := strings.ReplaceAll(username, "_", site.UnderscoreAs)
		if site.RegexCheck != "" {
			ok, err := regexp.MatchString(site.RegexCheck, e)
			if err != nil || !ok {
				return "", models.StatusIllegal
			}
		}
		return e, ""
	}

	if site.RegexCheck != "" {
		ok, err := regexp.MatchString(site.RegexCheck, username)
		if err != nil {
			return "", models.StatusIllegal
		}
		if ok {
			return username, ""
		}
		for _, rep := range []string{"-", "."} {
			e := strings.ReplaceAll(username, "_", rep)
			ok2, err2 := regexp.MatchString(site.RegexCheck, e)
			if err2 == nil && ok2 {
				return e, ""
			}
		}
		return "", models.StatusIllegal
	}

	return username, ""
}

func interpolate(template, username string) string {
	return strings.ReplaceAll(template, "{}", username)
}

func resolveMethod(site models.Site) string {
	if site.RequestMethod != "" {
		return strings.ToUpper(site.RequestMethod)
	}
	if len(site.RequestPayload) > 0 || site.RequestBody != "" {
		return http.MethodPost
	}
	return http.MethodGet
}

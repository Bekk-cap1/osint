package sites

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"github.com/user/hunter/internal/models"
)

type SiteEntry struct {
	URL           string            `json:"url"`
	URLMain       string            `json:"urlMain"`
	URLProbe      string            `json:"urlProbe,omitempty"`
	ErrorType     string            `json:"errorType"`
	ErrorMsg      interface{}       `json:"errorMsg,omitempty"`
	ErrorURL      string            `json:"errorUrl,omitempty"`
	RegexCheck    string            `json:"regexCheck,omitempty"`
	UnderscoreAs  string            `json:"underscoreAs,omitempty"`
	Countries     []string          `json:"countries"`
	Category      string            `json:"category,omitempty"`
	Headers          map[string]string `json:"headers,omitempty"`
	RequestMethod    string            `json:"request_method,omitempty"`
	RequestPayload   json.RawMessage   `json:"request_payload,omitempty"`
	RequestBody      string            `json:"requestBody,omitempty"`
	FoundSubstring   string            `json:"foundSubstring,omitempty"`
	NotFoundHTTP     int               `json:"notFoundHTTP,omitempty"`
	ExpectedHTTP     int               `json:"expectedHTTP,omitempty"`
}

func LoadSites(customPath string) ([]models.Site, error) {
	var path string
	if customPath != "" {
		path = customPath
	} else {
		path = findDataFile()
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("cannot read sites file: %w", err)
	}

	var raw map[string]SiteEntry
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("cannot parse sites file: %w", err)
	}

	sites := make([]models.Site, 0, len(raw))
	for name, entry := range raw {
		site := models.Site{
			Name:          name,
			URL:           entry.URL,
			URLMain:       entry.URLMain,
			URLProbe:      entry.URLProbe,
			ErrorType:     models.ErrorType(entry.ErrorType),
			ErrorURL:      entry.ErrorURL,
			RegexCheck:    entry.RegexCheck,
			UnderscoreAs:  entry.UnderscoreAs,
			Countries:     entry.Countries,
			Category:      entry.Category,
			Headers:          entry.Headers,
			RequestMethod:    entry.RequestMethod,
			RequestPayload:   entry.RequestPayload,
			RequestBody:      entry.RequestBody,
			FoundSubstring:   entry.FoundSubstring,
			NotFoundHTTP:     entry.NotFoundHTTP,
			ExpectedHTTP:     entry.ExpectedHTTP,
		}

		switch v := entry.ErrorMsg.(type) {
		case string:
			site.ErrorMsg = []string{v}
		case []interface{}:
			for _, item := range v {
				if s, ok := item.(string); ok {
					site.ErrorMsg = append(site.ErrorMsg, s)
				}
			}
		}

		if len(site.Countries) == 0 {
			site.Countries = []string{"global"}
		}

		sites = append(sites, site)
	}

	return sites, nil
}

func FilterByCountry(sites []models.Site, country string) []models.Site {
	if country == "" || country == "all" {
		return sites
	}

	filtered := make([]models.Site, 0)
	for _, site := range sites {
		for _, c := range site.Countries {
			if c == "global" || c == country {
				filtered = append(filtered, site)
				break
			}
		}
	}
	return filtered
}

func findDataFile() string {
	// Try relative to executable
	ex, err := os.Executable()
	if err == nil {
		p := filepath.Join(filepath.Dir(ex), "data", "sites.json")
		if _, err := os.Stat(p); err == nil {
			return p
		}
	}

	// Try relative to source (for development)
	_, filename, _, _ := runtime.Caller(0)
	p := filepath.Join(filepath.Dir(filename), "..", "..", "data", "sites.json")
	if _, err := os.Stat(p); err == nil {
		return p
	}

	// Try current directory
	if _, err := os.Stat("data/sites.json"); err == nil {
		return "data/sites.json"
	}

	return "data/sites.json"
}

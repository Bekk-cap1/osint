package models

import (
	"encoding/json"
	"time"
)

type ErrorType string

const (
	ErrorTypeStatusCode   ErrorType = "status_code"
	ErrorTypeMessage      ErrorType = "message"
	ErrorTypeResponseURL  ErrorType = "response_url"
)

type QueryStatus string

const (
	StatusFound   QueryStatus = "found"
	StatusNotFound QueryStatus = "not_found"
	StatusError   QueryStatus = "error"
	StatusIllegal QueryStatus = "illegal"
	StatusWAF     QueryStatus = "waf"
	StatusUnknown QueryStatus = "unknown"
)

type Site struct {
	Name         string    `json:"name"`
	URL          string    `json:"url"`
	URLMain      string    `json:"urlMain"`
	URLProbe     string    `json:"urlProbe,omitempty"`
	ErrorType    ErrorType `json:"errorType"`
	ErrorMsg     []string  `json:"errorMsg,omitempty"`
	ErrorURL     string    `json:"errorUrl,omitempty"`
	RegexCheck   string    `json:"regexCheck,omitempty"`
	// UnderscoreAs: if non-empty, "_" in username is replaced with this rune for URL/probe (e.g. "-").
	UnderscoreAs string    `json:"underscoreAs,omitempty"`
	Countries    []string  `json:"countries"`
	Category     string    `json:"category,omitempty"`
	Headers           map[string]string `json:"headers,omitempty"`
	RequestMethod     string            `json:"request_method,omitempty"`
	RequestPayload    json.RawMessage   `json:"request_payload,omitempty"`
	// RequestBody: сырое тело запроса (form-urlencoded и т.д.), плейсхолдер {} = username
	RequestBody string `json:"requestBody,omitempty"`
	// FoundSubstring: for errorType message (WhatsMyName-style) — успех только если эта подстрока есть в ответе
	FoundSubstring string `json:"foundSubstring,omitempty"`
	// NotFoundHTTP: если код ответа совпадает — считаем «не найден» (напр. 302 из WMN)
	NotFoundHTTP int `json:"notFoundHTTP,omitempty"`
	// ExpectedHTTP: если не 0, успех только при этом коде (иначе not_found)
	ExpectedHTTP int `json:"expectedHTTP,omitempty"`
}

type Result struct {
	Site         string      `json:"site"`
	URL          string      `json:"url"`
	URLMain      string      `json:"urlMain"`
	Username     string      `json:"username"`
	Status       QueryStatus `json:"status"`
	HTTPStatus   int         `json:"httpStatus,omitempty"`
	ResponseTime float64     `json:"responseTime,omitempty"`
	Error        string      `json:"error,omitempty"`
	Country      []string    `json:"country,omitempty"`
	Category     string      `json:"category,omitempty"`
}

type ScanRequest struct {
	Usernames []string `json:"usernames"`
	Email     string   `json:"email,omitempty"`
	Phone     string   `json:"phone,omitempty"`
	FullName  string   `json:"fullName,omitempty"`
	Country   string   `json:"country"`
	Timeout   int      `json:"timeout"`
}

type ScanProgress struct {
	Total     int       `json:"total"`
	Completed int       `json:"completed"`
	Found     int       `json:"found"`
	Current   string    `json:"current"`
	StartedAt time.Time `json:"startedAt"`
}

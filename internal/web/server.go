package web

import (
	"context"
	"embed"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"net/http"
	"sync"
	"sync/atomic"
	"time"

	"github.com/gorilla/websocket"
	"github.com/user/hunter/internal/generator"
	"github.com/user/hunter/internal/models"
	"github.com/user/hunter/internal/scheduler"
	"github.com/user/hunter/internal/sites"
)

//go:embed static/*
var staticFiles embed.FS

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

type Server struct {
	allSites []models.Site
	workers  int
	timeout  time.Duration
}

func NewServer(allSites []models.Site, workers int, timeout time.Duration) *Server {
	return &Server{
		allSites: allSites,
		workers:  workers,
		timeout:  timeout,
	}
}

type wsMessage struct {
	Type    string      `json:"type"`
	Payload interface{} `json:"payload"`
}

type scanConn struct {
	mu          sync.Mutex
	cancel      context.CancelFunc
	activeRunID int64
}

var scanRunSeq int64

func (s *Server) Start(port int) error {
	mux := http.NewServeMux()

	staticFS, _ := fs.Sub(staticFiles, "static")
	mux.Handle("/", http.FileServer(http.FS(staticFS)))
	mux.HandleFunc("/ws", s.handleWebSocket)
	mux.HandleFunc("/api/countries", s.handleCountries)
	mux.HandleFunc("/api/sites", s.handleSites)

	addr := fmt.Sprintf(":%d", port)
	fmt.Printf("[*] Web dashboard: http://localhost%s\n", addr)
	return http.ListenAndServe(addr, mux)
}

func (s *Server) handleCountries(w http.ResponseWriter, r *http.Request) {
	countries := make(map[string]bool)
	for _, site := range s.allSites {
		for _, c := range site.Countries {
			countries[c] = true
		}
	}
	list := make([]string, 0, len(countries))
	for c := range countries {
		list = append(list, c)
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(list)
}

func (s *Server) handleSites(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]int{"total": len(s.allSites)})
}

func (s *Server) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}
	defer conn.Close()

	var writeMu sync.Mutex
	sc := &scanConn{}
	defer func() {
		sc.mu.Lock()
		if sc.cancel != nil {
			sc.cancel()
		}
		sc.mu.Unlock()
	}()

	for {
		_, msg, err := conn.ReadMessage()
		if err != nil {
			return
		}

		var head struct {
			Op string `json:"op"`
		}
		if err := json.Unmarshal(msg, &head); err != nil {
			sendWSMessage(conn, &writeMu, "error", map[string]string{"message": "invalid json"})
			continue
		}
		if head.Op == "stop" {
			sc.mu.Lock()
			if sc.cancel != nil {
				sc.cancel()
			}
			sc.mu.Unlock()
			continue
		}

		var req models.ScanRequest
		if err := json.Unmarshal(msg, &req); err != nil {
			sendWSMessage(conn, &writeMu, "error", map[string]string{"message": "invalid request"})
			continue
		}

		go s.runScan(conn, &writeMu, req, sc)
	}
}

func (s *Server) runScan(conn *websocket.Conn, writeMu *sync.Mutex, req models.ScanRequest, sc *scanConn) {
	var mu sync.Mutex

	var usernames []string
	if len(req.Usernames) > 0 {
		for _, u := range req.Usernames {
			usernames = append(usernames, generator.GenerateFromUsername(u)...)
		}
	}
	if req.FullName != "" {
		usernames = append(usernames, generator.GenerateFromFullName(req.FullName)...)
	}
	if req.Email != "" {
		usernames = append(usernames, generator.GenerateFromEmail(req.Email)...)
	}
	if req.Phone != "" {
		usernames = append(usernames, generator.GenerateFromPhone(req.Phone)...)
	}

	if len(usernames) == 0 {
		sendWSMessage(conn, writeMu, "error", map[string]string{"message": "no usernames to check"})
		return
	}

	filteredSites := sites.FilterByCountry(s.allSites, req.Country)

	total := len(filteredSites) * len(usernames)
	sendWSMessage(conn, writeMu, "start", map[string]interface{}{
		"total":     total,
		"usernames": usernames,
		"sites":     len(filteredSites),
		"country":   req.Country,
	})

	timeout := time.Duration(req.Timeout) * time.Second
	if timeout <= 0 {
		timeout = s.timeout
	}

	ctx, cancel := context.WithCancel(context.Background())
	runID := atomic.AddInt64(&scanRunSeq, 1)
	sc.mu.Lock()
	if sc.cancel != nil {
		sc.cancel()
	}
	sc.cancel = cancel
	sc.activeRunID = runID
	sc.mu.Unlock()

	defer func() {
		sc.mu.Lock()
		if sc.activeRunID == runID {
			sc.cancel = nil
		}
		sc.mu.Unlock()
		cancel()
	}()

	sched := scheduler.New(s.workers, timeout)
	completed := 0

	sched.OnResult = func(result models.Result) {
		mu.Lock()
		completed++
		c := completed
		mu.Unlock()

		if result.Status == models.StatusFound {
			sendWSMessage(conn, writeMu, "found", result)
		}
		sendWSMessage(conn, writeMu, "progress", map[string]interface{}{
			"completed": c,
			"total":     total,
		})
	}

	results := sched.Run(ctx, filteredSites, usernames)

	stopped := errors.Is(ctx.Err(), context.Canceled)
	if stopped {
		found := 0
		for _, r := range results {
			if r.Status == models.StatusFound {
				found++
			}
		}
		sendWSMessage(conn, writeMu, "stopped", map[string]interface{}{
			"checked": len(results),
			"total":   total,
			"found":   found,
		})
		return
	}

	found := 0
	for _, r := range results {
		if r.Status == models.StatusFound {
			found++
		}
	}
	sendWSMessage(conn, writeMu, "done", map[string]interface{}{
		"total": total,
		"found": found,
	})
}

func sendWSMessage(conn *websocket.Conn, writeMu *sync.Mutex, msgType string, payload interface{}) {
	msg := wsMessage{Type: msgType, Payload: payload}
	data, _ := json.Marshal(msg)
	writeMu.Lock()
	_ = conn.WriteMessage(websocket.TextMessage, data)
	writeMu.Unlock()
}

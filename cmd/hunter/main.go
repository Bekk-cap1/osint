package main

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"sync"
	"time"

	"github.com/fatih/color"
	"github.com/mattn/go-isatty"
	"github.com/user/hunter/internal/generator"
	"github.com/user/hunter/internal/models"
	"github.com/user/hunter/internal/scheduler"
	"github.com/user/hunter/internal/sites"
	"github.com/user/hunter/internal/web"
)

var (
	version = "0.2.0"
)

func main() {
	var phone string
	username := flag.String("u", "", "Username to search")
	fullName := flag.String("n", "", "Full name to generate username variations")
	email := flag.String("e", "", "Email to search (local part + Gravatar MD5)")
	flag.StringVar(&phone, "phone", "", "Phone digits only (WhatsApp / phone-specific sites in sites.json)")
	flag.StringVar(&phone, "p", "", "Shorthand for -phone")
	country := flag.String("country", "all", "Country filter (uz, ru, cn, all)")
	output := flag.String("o", "", "Output file (JSON)")
	csvFlag := flag.Bool("csv", false, "Export as CSV")
	timeout := flag.Int("timeout", 30, "Timeout per request in seconds")
	workers := flag.Int("workers", 50, "Number of concurrent workers")
	webMode := flag.Bool("web", false, "Start web dashboard")
	webPort := flag.Int("port", 8080, "Web dashboard port")
	sitesPath := flag.String("sites", "", "Path to sites.json (по умолчанию data/sites.json рядом с .exe или исходниками)")
	verbose := flag.Bool("v", false, "Verbose output")
	showVersion := flag.Bool("version", false, "Show version")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `
  ╦ ╦╦ ╦╔╗╔╔╦╗╔═╗╦═╗
  ╠═╣║ ║║║║ ║ ║╣ ╠╦╝
  ╩ ╩╚═╝╝╚╝ ╩ ╚═╝╩╚═  v%s

  OSINT Username Hunter — Sherlock-style + большой sites.json (WMN и др.). Свой файл: -sites path.
  Автор: @bekk_cap1 

`, version)
		fmt.Fprintf(os.Stderr, "Usage:\n")
		fmt.Fprintf(os.Stderr, "  hunter <username>                   Поиск по нику\n")
		fmt.Fprintf(os.Stderr, "  hunter u1 u2                        Несколько ников\n")
		fmt.Fprintf(os.Stderr, "  hunter -u x -e a@b -p 7900…       Скомбинировать email, телефон, ник\n")
		fmt.Fprintf(os.Stderr, "  hunter -n \"First Last\"            Варианты из ФИО\n")
		fmt.Fprintf(os.Stderr, "  hunter -e user@mail.com            Email → локальная часть + MD5 (Gravatar_*)\n")
		fmt.Fprintf(os.Stderr, "  hunter -p 79991234567              Цифры телефона (Phone_* в базе)\n")
		fmt.Fprintf(os.Stderr, "  hunter nick -country uz            Фильтр страны (+ global)\n")
		fmt.Fprintf(os.Stderr, "  hunter -web [-port 8080]           Веб-панель\n\n")
		fmt.Fprintf(os.Stderr, "Flags:\n")
		flag.PrintDefaults()
	}

	flag.Parse()

	// Positional arguments as usernames (like sherlock)
	if len(flag.Args()) > 0 && *username == "" && *fullName == "" && *email == "" && phone == "" && !*webMode && !*showVersion {
		*username = flag.Args()[0]
	}

	if *showVersion {
		fmt.Printf("hunter v%s\n", version)
		return
	}

	// Load sites
	allSites, err := sites.LoadSites(*sitesPath)
	if err != nil {
		color.Red("[!] Failed to load sites: %v", err)
		os.Exit(1)
	}

	// Web mode
	if *webMode {
		color.Cyan("[*] Starting web dashboard on port %d (%d sites in DB)...", *webPort, len(allSites))
		srv := web.NewServer(allSites, *workers, time.Duration(*timeout)*time.Second)
		if err := srv.Start(*webPort); err != nil {
			color.Red("[!] Web server error: %v", err)
			os.Exit(1)
		}
		return
	}

	// Determine usernames to check (можно комбинировать имя, email, телефон, ник)
	var usernames []string
	if *fullName != "" {
		usernames = append(usernames, generator.GenerateFromFullName(*fullName)...)
	}
	if *email != "" {
		usernames = append(usernames, generator.GenerateFromEmail(*email)...)
	}
	if phone != "" {
		usernames = append(usernames, generator.GenerateFromPhone(phone)...)
	}
	if *username != "" {
		usernames = append(usernames, generator.GenerateFromUsername(*username)...)
	}
	for _, a := range flag.Args() {
		if a == *username {
			continue
		}
		usernames = append(usernames, generator.GenerateFromUsername(a)...)
	}
	if len(usernames) == 0 {
		flag.Usage()
		os.Exit(1)
	}

	// Filter sites by country
	filteredSites := sites.FilterByCountry(allSites, *country)

	color.Cyan("[*] Hunter v%s", version)
	color.White("[*] База: %d сайтов → после фильтра «%s»: %d | вариантов имён: %d",
		len(allSites), *country, len(filteredSites), len(usernames))
	if *verbose {
		color.White("[*] Usernames: %s", strings.Join(usernames, ", "))
	}
	fmt.Println()

	// Setup context with signal handling
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt)
	go func() {
		<-sigCh
		color.Yellow("\n[!] Interrupted, stopping...")
		cancel()
	}()

	// Run scanner
	green := color.New(color.FgGreen).SprintfFunc()
	red := color.New(color.FgRed).SprintfFunc()
	_ = red

	sched := scheduler.New(*workers, time.Duration(*timeout)*time.Second)

	var found []models.Result
	var termMu sync.Mutex
	stderrTTY := isatty.IsTerminal(os.Stderr.Fd())

	totalJobs := len(filteredSites) * len(usernames)
	progressStep := totalJobs / 50
	if progressStep < 1 {
		progressStep = 1
	}
	sched.OnProgress = func(done, tot int) {
		if tot == 0 {
			return
		}
		if done != tot && done != 1 && done%progressStep != 0 {
			return
		}
		pct := 100.0 * float64(done) / float64(tot)
		termMu.Lock()
		defer termMu.Unlock()
		if stderrTTY {
			fmt.Fprintf(os.Stderr, "\r\x1b[K[*] Progress: %d / %d (%.1f%%)", done, tot, pct)
		} else {
			fmt.Fprintf(os.Stderr, "[*] Progress: %d / %d (%.1f%%)\n", done, tot, pct)
		}
	}

	sched.OnResult = func(result models.Result) {
		termMu.Lock()
		defer termMu.Unlock()
		switch result.Status {
		case models.StatusFound:
			found = append(found, result)
			if stderrTTY {
				fmt.Fprintf(os.Stderr, "\r\x1b[K\n")
			}
			fmt.Printf(" %s %s — %s\n", green("[+]"), result.Site, result.URL)
		case models.StatusError:
			if *verbose {
				if stderrTTY {
					fmt.Fprintf(os.Stderr, "\r\x1b[K\n")
				}
				fmt.Printf(" [!] %s — %s\n", result.Site, result.Error)
			}
		case models.StatusWAF:
			if *verbose {
				if stderrTTY {
					fmt.Fprintf(os.Stderr, "\r\x1b[K\n")
				}
				fmt.Printf(" [W] %s — WAF detected\n", result.Site)
			}
		}
	}

	startTime := time.Now()
	results := sched.Run(ctx, filteredSites, usernames)
	fmt.Fprintln(os.Stderr)
	elapsed := time.Since(startTime)

	// Summary
	fmt.Println()
	foundCount := 0
	for _, r := range results {
		if r.Status == models.StatusFound {
			foundCount++
		}
	}
	color.Cyan("[*] Done in %.1fs — %d/%d accounts found", elapsed.Seconds(), foundCount, len(results))

	// Export
	if *output != "" {
		exportJSON(*output, found)
		color.Green("[+] Results saved to %s", *output)
	}
	if *csvFlag {
		base := "results"
		switch {
		case *username != "":
			base = *username
		case phone != "":
			base = "phone_" + phone
		case *email != "":
			local := *email
			if i := strings.Index(local, "@"); i > 0 {
				local = local[:i]
			}
			base = local
		}
		filename := base + ".csv"
		exportCSV(filename, found)
		color.Green("[+] CSV saved to %s", filename)
	}
}

func exportJSON(path string, results []models.Result) {
	data, _ := json.MarshalIndent(results, "", "  ")
	os.WriteFile(path, data, 0644)
}

func exportCSV(path string, results []models.Result) {
	f, err := os.Create(path)
	if err != nil {
		return
	}
	defer f.Close()

	w := csv.NewWriter(f)
	defer w.Flush()

	w.Write([]string{"Site", "URL", "Username", "Status", "Response Time"})
	for _, r := range results {
		w.Write([]string{
			r.Site,
			r.URL,
			r.Username,
			string(r.Status),
			fmt.Sprintf("%.2fs", r.ResponseTime),
		})
	}
}

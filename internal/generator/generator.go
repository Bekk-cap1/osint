package generator

import (
	"crypto/md5"
	"fmt"
	"strings"
)

var separators = []string{"_", "-", "."}
var commonYears = []string{"1", "01", "99", "00", "123", "777"}

func GenerateFromFullName(fullName string) []string {
	parts := strings.Fields(strings.ToLower(strings.TrimSpace(fullName)))
	if len(parts) == 0 {
		return nil
	}

	var results []string
	seen := make(map[string]bool)

	add := func(s string) {
		if s != "" && !seen[s] {
			seen[s] = true
			results = append(results, s)
		}
	}

	if len(parts) == 1 {
		add(parts[0])
		for _, y := range commonYears {
			add(parts[0] + y)
		}
		return results
	}

	first := parts[0]
	last := parts[len(parts)-1]
	firstInitial := string(first[0])
	lastInitial := string(last[0])

	// Full combinations
	for _, sep := range separators {
		add(first + sep + last)
		add(last + sep + first)
		add(firstInitial + sep + last)
		add(last + sep + firstInitial)
		add(first + sep + lastInitial)
		add(lastInitial + sep + first)
	}

	// No separator
	add(first + last)
	add(last + first)
	add(firstInitial + last)
	add(last + firstInitial)
	add(first + lastInitial)
	add(lastInitial + first)

	// Short forms
	add(first)
	add(last)

	// With numbers
	bases := []string{
		first + "_" + last,
		last + "_" + first,
		first + last,
		last + first,
		firstInitial + last,
		firstInitial + "_" + last,
	}
	for _, base := range bases {
		for _, y := range commonYears {
			add(base + y)
		}
	}

	// If 3 parts (first middle last)
	if len(parts) >= 3 {
		middle := parts[1]
		middleInitial := string(middle[0])
		for _, sep := range separators {
			add(first + sep + middle + sep + last)
			add(firstInitial + sep + middleInitial + sep + last)
			add(first + sep + middleInitial + sep + last)
		}
		add(first + middle + last)
		add(firstInitial + middleInitial + last)
	}

	return results
}

func GenerateFromUsername(username string) []string {
	return []string{strings.ToLower(strings.TrimSpace(username))}
}

func GravatarMD5Hex(email string) string {
	e := strings.TrimSpace(strings.ToLower(email))
	if e == "" {
		return ""
	}
	return fmt.Sprintf("%x", md5.Sum([]byte(e)))
}

func GenerateFromEmail(email string) []string {
	var results []string
	seen := make(map[string]bool)

	add := func(s string) {
		if s != "" && !seen[s] {
			seen[s] = true
			results = append(results, s)
		}
	}

	email = strings.ToLower(strings.TrimSpace(email))
	add(email)

	atIdx := strings.Index(email, "@")
	if atIdx > 0 {
		localPart := email[:atIdx]
		add(localPart)

		if h := GravatarMD5Hex(email); h != "" {
			add(h)
		}

		// Try splitting local part by common separators
		for _, sep := range separators {
			if strings.Contains(localPart, sep) {
				parts := strings.Split(localPart, sep)
				if len(parts) >= 2 {
					add(strings.Join(parts, ""))
					add(strings.Join(parts, "_"))
					add(strings.Join(parts, "."))
					add(strings.Join(parts, "-"))
				}
			}
		}

		// Remove trailing digits
		trimmed := strings.TrimRight(localPart, "0123456789")
		if trimmed != localPart && trimmed != "" {
			add(trimmed)
		}
	}

	return results
}

// GenerateFromPhone возвращает нормализованные цифровые варианты (WA / подбор без '+').
func GenerateFromPhone(phone string) []string {
	var b strings.Builder
	for _, r := range strings.TrimSpace(phone) {
		if r >= '0' && r <= '9' {
			b.WriteRune(r)
		}
	}
	d := b.String()
	if d == "" {
		return nil
	}

	seen := make(map[string]bool)
	var out []string
	add := func(s string) {
		if s != "" && !seen[s] {
			seen[s] = true
			out = append(out, s)
		}
	}

	add(d)
	if strings.HasPrefix(d, "00") && len(d) > 4 {
		add(d[2:])
	}
	if len(d) >= 11 && d[0] == '0' {
		add(d[1:])
	}
	return out
}

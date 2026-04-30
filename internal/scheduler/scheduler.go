package scheduler

import (
	"context"
	"sync"
	"time"

	"github.com/user/hunter/internal/checker"
	"github.com/user/hunter/internal/models"
)

type ResultCallback func(result models.Result)

type Scheduler struct {
	Workers    int
	Timeout    time.Duration
	OnResult   ResultCallback
	OnProgress func(completed, total int)
}

func New(workers int, timeout time.Duration) *Scheduler {
	if workers <= 0 {
		workers = 50
	}
	if timeout <= 0 {
		timeout = 30 * time.Second
	}
	return &Scheduler{
		Workers: workers,
		Timeout: timeout,
	}
}

func (s *Scheduler) Run(ctx context.Context, sites []models.Site, usernames []string) []models.Result {
	type job struct {
		site     models.Site
		username string
	}

	jobs := make(chan job, s.Workers*4)
	resultsCh := make(chan models.Result, 100)

	var wg sync.WaitGroup
	var results []models.Result
	var mu sync.Mutex
	total := len(sites) * len(usernames)
	completed := 0

	for i := 0; i < s.Workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				if ctx.Err() != nil {
					continue
				}
				timeoutCtx, cancel := context.WithTimeout(ctx, s.Timeout)
				result := checker.CheckSite(timeoutCtx, j.site, j.username, s.Timeout)
				cancel()
				resultsCh <- result
			}
		}()
	}

	done := make(chan struct{})
	go func() {
		for result := range resultsCh {
			mu.Lock()
			results = append(results, result)
			completed++
			c := completed
			mu.Unlock()

			if s.OnResult != nil {
				s.OnResult(result)
			}
			if s.OnProgress != nil {
				s.OnProgress(c, total)
			}
		}
		close(done)
	}()

	go func() {
		defer close(jobs)
	outer:
		for _, username := range usernames {
			for _, si := range sites {
				select {
				case <-ctx.Done():
					break outer
				case jobs <- job{site: si, username: username}:
				}
			}
		}
	}()

	wg.Wait()
	close(resultsCh)
	<-done

	return results
}

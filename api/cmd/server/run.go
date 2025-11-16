package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/zlicdt/docker-nocli/api/internal/api"
	"github.com/zlicdt/docker-nocli/api/internal/config"
	internaldocker "github.com/zlicdt/docker-nocli/api/internal/docker"
	"github.com/zlicdt/docker-nocli/api/internal/store"
	"go.uber.org/zap"
)

func run() error {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("load config: %w", err)
	}

	logger, err := zap.NewProduction()
	if err != nil {
		return fmt.Errorf("init logger: %w", err)
	}
	defer logger.Sync() //nolint:errcheck // ignoring sync errors on exit

	dockerClient, err := internaldocker.New(cfg.DockerHost)
	if err != nil {
		return fmt.Errorf("init docker client: %w", err)
	}
	defer dockerClient.Close() //nolint:errcheck

	deps := api.Dependencies{
		Store:  store.NewInMemoryStore(),
		Docker: dockerClient,
		Logger: logger,
	}

	router, err := api.NewRouter(deps)
	if err != nil {
		return fmt.Errorf("init router: %w", err)
	}

	server := &http.Server{
		Addr:    cfg.Address,
		Handler: router,
	}

	serverErr := make(chan error, 1)
	go func() {
		logger.Info("server starting", zap.String("addr", cfg.Address))
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			serverErr <- err
			return
		}
		serverErr <- nil
	}()

	select {
	case <-ctx.Done():
		logger.Info("shutdown signal received")
	case err := <-serverErr:
		if err != nil {
			return fmt.Errorf("server error: %w", err)
		}
		return nil
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("server shutdown: %w", err)
	}

	logger.Info("server stopped gracefully")
	return nil
}

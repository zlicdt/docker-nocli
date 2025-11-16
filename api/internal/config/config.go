package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config aggregates all runtime configuration for the API server.
type Config struct {
	// Address is the HTTP listen address, ex: ":8080" or "127.0.0.1:9000".
	Address string
	// DockerHost points to the Docker daemon socket or TCP endpoint.
	// You can setup manually, but the default is unix:///var/run/docker.sock
	DockerHost string
}

// Load reads configuration from the environment, applying defaults when needed.
func Load() (*Config, error) {
	cfg := &Config{
		Address:    resolveAddress(),
		DockerHost: resolveDockerHost(),
	}

	if strings.TrimSpace(cfg.Address) == "" {
		return nil, fmt.Errorf("address cannot be empty")
	}

	return cfg, nil
}

func resolveAddress() string {
	// The port should place in API_PORT or PORT.
	// Priority of API_PORT is bigger than PORT
	if port := firstNonEmpty(os.Getenv("API_PORT"), os.Getenv("PORT")); port != "" {
		if _, err := strconv.Atoi(port); err == nil {
			return fmt.Sprintf(":%s", port)
		}
	}

	return ":8080"
}

func resolveDockerHost() string {
	if host := strings.TrimSpace(os.Getenv("DOCKER_HOST")); host != "" {
		return host
	}

	return "unix:///var/run/docker.sock"
}

// This func for resolveAddress()
func firstNonEmpty(values ...string) string {
	for _, v := range values {
		if strings.TrimSpace(v) != "" {
			return strings.TrimSpace(v)
		}
	}

	return ""
}

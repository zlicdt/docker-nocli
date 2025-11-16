package docker

import (
	"context"
	"fmt"

	"github.com/moby/moby/client"
)

// Client wraps the official Docker client to allow future extensions.
type Client struct {
	*client.Client
}

// New creates a Docker client using the provided host or the defaults from the environment.
func New(host string) (*Client, error) {
	opts := []client.Opt{
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
		client.WithHost(host),
	}

	cli, err := client.New(opts...)
	if err != nil {
		return nil, fmt.Errorf("create docker client: %w", err)
	}

	return &Client{Client: cli}, nil
}

// Health pings the Docker daemon to ensure it is reachable.
func (c *Client) Health(ctx context.Context) error {
	if c == nil || c.Client == nil {
		return fmt.Errorf("docker client is not initialized")
	}

	_, err := c.Ping(ctx, client.PingOptions{NegotiateAPIVersion: true, ForceNegotiate: false})
	if err != nil {
		return fmt.Errorf("docker ping failed: %w", err)
	}

	return nil
}

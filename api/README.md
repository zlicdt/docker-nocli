# Docker WebUI API

This folder contains the Go API server that powers the Docker WebUI project. The service exposes a REST API backed by Gin and talks to the local Docker daemon.

## Requirements

- Go 1.25+
- Access to a Docker Engine socket (default: `/var/run/docker.sock`)

## Configuration

Configuration is environment-driven:

| Variable      | Default                         | Description                                      |
| ------------- | -------------------------------- | ------------------------------------------------ |
| `API_ADDR`    | `:${PORT}` or `:8080`            | HTTP listen address (overrides port variables).  |
| `PORT`        | `8080`                           | Used when `API_ADDR` is empty.                   |
| `DOCKER_HOST` | `unix:///var/run/docker.sock`    | Docker daemon host/socket.                       |

## Run locally

```bash
cd api
go run ./cmd/server
```

The server exposes a `/healthz` endpoint verifying the store and Docker connectivity.

## Tests

```bash
cd api
go test ./...
```

Run the tests before committing changes to catch regressions early.

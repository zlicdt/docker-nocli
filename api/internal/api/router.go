package api

import (
	"fmt"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	internaldocker "github.com/zlicdt/docker-nocli/api/internal/docker"
	"github.com/zlicdt/docker-nocli/api/internal/store"
)

// Dependencies enumerates the services required to build the HTTP router.
type Dependencies struct {
	Store  store.Store
	Docker *internaldocker.Client
	Logger *zap.Logger
}

func (d Dependencies) validate() error {
	if d.Store == nil {
		return fmt.Errorf("store dependency is required")
	}

	if d.Docker == nil {
		return fmt.Errorf("docker dependency is required")
	}

	if d.Logger == nil {
		return fmt.Errorf("logger dependency is required")
	}

	return nil
}

// NewRouter constructs a Gin engine with the initial set of routes.
func NewRouter(deps Dependencies) (*gin.Engine, error) {
	if err := deps.validate(); err != nil {
		return nil, err
	}

	router := gin.New()
	router.Use(gin.Recovery())

	handler := NewHandler(deps)
	handler.registerRoutes(router)

	return router, nil
}

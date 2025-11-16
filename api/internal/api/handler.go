package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	internaldocker "github.com/zlicdt/docker-nocli/api/internal/docker"
	"github.com/zlicdt/docker-nocli/api/internal/store"
)

// Handler aggregates dependencies for HTTP handlers.
type Handler struct {
	store  store.Store
	docker *internaldocker.Client
	logger *zap.Logger
}

// NewHandler builds a Handler from the given dependencies.
func NewHandler(deps Dependencies) *Handler {
	return &Handler{
		store:  deps.Store,
		docker: deps.Docker,
		logger: deps.Logger,
	}
}

func (h *Handler) registerRoutes(router *gin.Engine) {
	router.GET("/healthz", h.health)
}

func (h *Handler) health(c *gin.Context) {
	ctx := c.Request.Context()

	if err := h.store.Health(ctx); err != nil {
		h.logger.Error("store health failed", zap.Error(err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"status": "degraded", "error": err.Error()})
		return
	}

	if err := h.docker.Health(ctx); err != nil {
		h.logger.Error("docker health failed", zap.Error(err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"status": "degraded", "error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

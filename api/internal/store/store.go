package store

import "context"

// Store abstracts configuration persistence for future expansion.
type Store interface {
	Health(ctx context.Context) error
}

// InMemoryStore is a placeholder implementation used during bootstrap.
type InMemoryStore struct{}

// NewInMemoryStore returns a store that always reports healthy.
func NewInMemoryStore() Store {
	return &InMemoryStore{}
}

// Health always returns nil, indicating the store is reachable.
func (s *InMemoryStore) Health(ctx context.Context) error {
	return nil
}

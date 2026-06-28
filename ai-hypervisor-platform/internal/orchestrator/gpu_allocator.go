package orchestrator

import (
	"context"
	"github.com/DARREN-2000/ai-hypervisor-platform/internal/models"
)

// GPUOrchestrator handles GPU allocation and management
type GPUOrchestrator interface {
	// AllocateGPU allocates GPUs to a VM
	AllocateGPU(ctx context.Context, vmID string, requests []models.GPURequest) ([]models.GPUAllocation, error)

	// DeallocateGPU releases allocated GPUs
	DeallocateGPU(ctx context.Context, vmID string) error

	// GetGPUAvailability returns available GPUs
	GetGPUAvailability(ctx context.Context) ([]*models.GPU, error)

	// GetGPUByID retrieves GPU details
	GetGPUByID(ctx context.Context, gpuID string) (*models.GPU, error)

	// UpdateGPUMetrics updates GPU telemetry data
	UpdateGPUMetrics(ctx context.Context, gpuID string, metrics *models.GPUMetrics) error

	// CheckGPUHealth performs health checks on GPUs
	CheckGPUHealth(ctx context.Context, nodeID string) error
}

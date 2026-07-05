package orchestrator

import (
	"context"

	"github.com/DARREN-2000/ai-hypervisor-platform/internal/models"
)

type SchedulingMetrics struct {}

// VMScheduler interface handles virtual machine placement and lifecycle
type VMScheduler interface {
	Schedule(ctx context.Context, vm *models.VirtualMachine) (*models.SchedulingDecision, error)

	// Unschedule removes a VM from its current host
	Unschedule(ctx context.Context, decisionID string) error

	// Preempt attempts to find a higher priority placement
	Preempt(ctx context.Context, target string) (*models.SchedulingDecision, error)

	// GetMetrics returns current cluster utilization statistics
	GetMetrics(ctx context.Context) (*SchedulingMetrics, error)
}

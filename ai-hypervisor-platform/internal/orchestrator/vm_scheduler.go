package orchestrator

import (
	"context"
	"github.com/DARREN-2000/ai-hypervisor-platform/internal/models"
)

// Scheduler handles VM placement decisions
type Scheduler interface {
	// ScheduleVM makes a placement decision for a VM
	ScheduleVM(ctx context.Context, vm *models.VirtualMachine) (*models.SchedulingDecision, error)

	// RescheduleVM attempts to reschedule a VM to a different host
	RescheduleVM(ctx context.Context, vmID string) (*models.SchedulingDecision, error)

	// CheckNodeCapacity checks if a node can accommodate a VM
	CheckNodeCapacity(ctx context.Context, nodeID string, resources models.VMFlavor) bool

	// GetSchedulingMetrics returns current scheduling metrics
	GetSchedulingMetrics(ctx context.Context) (*SchedulingMetrics, error)
}

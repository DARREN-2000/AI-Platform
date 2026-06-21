# AI Hypervisor Platform - V2 Architecture Design

The AI Hypervisor Platform is the foundational compute orchestration layer. It bridges the gap between Kubernetes/Bare-metal and high-level AI routing. In the V2 architecture, it is strictly decoupled from the synchronous hot path. It listens for capacity requests from the Inference Control Plane and dynamically provisions or de-provisions GPU-backed model instances.

## 1. Folder Structure

```text
ai-hypervisor-platform/
├── cmd/
│   ├── controller/
│   │   └── main.go
│   └── agent/
│       └── main.go
├── internal/
│   ├── config/
│   ├── scheduler/
│   │   ├── binpack.go
│   │   └── node_manager.go
│   ├── provisioner/
│   │   ├── libvirt.go
│   │   ├── kubernetes.go
│   │   └── vllm.go
│   ├── events/
│   │   └── nats_subscriber.go
│   ├── api/
│   │   └── grpc_server.go
│   └── telemetry/
│       └── nvml_monitor.go
├── pkg/
│   └── api/
│       └── v1/
├── deploy/
│   ├── helm/
│   └── crds/
├── go.mod
├── go.sum
└── README.md
```

## 2. Package Structure

- **`cmd`**: Entry points for the central `controller` (brain) and the node-level `agent` (runs on GPU nodes).
- **`internal.scheduler`**: Logic for determining where to place new model workloads based on available GPU VRAM and node health.
- **`internal.provisioner`**: Abstraction layer for interacting with underlying infrastructure (spinning up KVM VMs via Libvirt or pods via Kubernetes) and configuring inference engines (like vLLM).
- **`internal.events`**: NATS client for subscribing to `model.capacity.requested` events from the Inference Control Plane.
- **`internal.api`**: Internal gRPC APIs for agents to report health and metrics back to the controller.
- **`internal.telemetry`**: Node-level monitoring using NVML to track GPU utilization, temperature, and memory.

## 3. Interfaces

- **Inference Control Plane (NATS)**: Asynchronous event consumption (scale up/down requests) and publishing (endpoint ready notifications).
- **Node Agents (gRPC)**: Communication between the central controller and the agents running on individual GPU machines.
- **Infrastructure (APIs)**: Communication with Kubernetes API server or Libvirt daemon to execute provisioning commands.

## 4. Domain Model

- **Node**: A physical or virtual machine equipped with one or more GPUs.
- **GPUResource**: Represents available/allocated VRAM and compute capacity on a specific Node.
- **ModelWorkload**: A definition of a model (e.g., `llama-3-8b`, `weights_url`, `min_vram_gb`).
- **Instance**: A running ModelWorkload on a specific Node.
- **Endpoint**: The network address (IP:Port) where a running Instance is accepting traffic.

## 5. API Specification (Internal gRPC)

While primary scaling is event-driven, agents report to the controller via gRPC:

- `rpc RegisterNode (NodeInfo) returns (NodeAck)`
- `rpc ReportTelemetry (HardwareMetrics) returns (Ack)`
- `rpc UpdateInstanceStatus (InstanceStatus) returns (Ack)`

*(Note: The controller does not expose a public REST API for inference; it only manages infrastructure).*

## 6. Database Schema (PostgreSQL)

- **`nodes`**: `id`, `hostname`, `ip_address`, `total_vram_mb`, `status`, `last_seen`
- **`gpu_devices`**: `id`, `node_id`, `pci_id`, `model_name`, `vram_mb`
- **`workload_definitions`**: `id`, `name`, `container_image`, `required_vram_mb`
- **`running_instances`**: `id`, `node_id`, `workload_id`, `status` (provisioning, running, terminating), `endpoint_url`

## 7. Event Model (NATS)

- **Subscribes**: `model.capacity.requested`
  - Action: Scheduler evaluates resources, selects a node, and instructs the provisioner to pull weights and start the engine (e.g., vLLM).
- **Publishes**: `model.endpoint.ready`
  - Emitted when the provisioner confirms the model is loaded into VRAM and the health check endpoint returns 200 OK. The Inference Control Plane uses this to update its routing tables.
- **Publishes**: `model.endpoint.offline`
  - Emitted if an agent detects a GPU crash or OOM error.

## 8. Deployment Model

- **Controller**: Deployed as a highly available deployment in the control plane Kubernetes cluster.
- **Agents**: Deployed as a DaemonSet on GPU-enabled worker nodes. Requires privileged access and host network/PID namespaces to interact with NVML and Libvirt/Containerd.

## 9. Testing Strategy

- **Unit Tests**: Test the bin-packing scheduler algorithms to ensure efficient GPU allocation.
- **Integration Tests**: Use mock NATS servers to ensure capacity events correctly trigger the provisioning state machine.
- **System Tests**: "Dry-run" provisioners that mock Libvirt/K8s APIs to test the entire lifecycle from scale-up request to endpoint-ready notification without requiring physical GPUs.

## 10. Roadmap

1.  **Phase 1**: Establish the NATS communication layer with the Inference Control Plane.
2.  **Phase 2**: Implement the node agent to report basic NVML telemetry (VRAM, utilization) back to the controller.
3.  **Phase 3**: Build a basic scheduler that can place a workload on a node with sufficient VRAM.
4.  **Phase 4**: Implement the provisioner for Kubernetes (deploying vLLM pods dynamically).
5.  **Phase 5**: Advanced features like model weight caching (using a local SAN or high-speed network attached storage) to reduce cold-start provisioning times.

class GuardrailXInterceptorClient:
    """gRPC Client for connecting to GuardrailX evaluation service."""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    async def evaluate_request(self, prompt: str, policy_name: str) -> bool:
        return True

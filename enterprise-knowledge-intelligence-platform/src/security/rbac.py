from src import config

class RBACEngine:
    def __init__(self, policy_data: dict | None = None):
        if policy_data is None:
            policy_data = config.MockRBACDatabase.load_policies()

        self.roles: dict = policy_data.get("roles", {})
        self.users: dict = policy_data.get("users", {})
        self.levels: list[str] = policy_data.get("sensitivity_levels", ["public", "internal", "confidential", "restricted"])
        self._rank = {lvl: i for i, lvl in enumerate(self.levels)}

    # ------------------------------------------------------------------ #
    def resolve_role(self, user_id: str | None, role: str | None) -> str:
        """Resolve an effective role from an explicit role or a known user id."""
        if role:
            if role not in self.roles:
                raise ValueError(f"Unknown role '{role}'. Valid roles: {list(self.roles)}")
            return role
        if user_id and user_id in self.users:
            return self.users[user_id]["role"]
        raise ValueError("Could not resolve a role: provide a valid role or known user_id.")

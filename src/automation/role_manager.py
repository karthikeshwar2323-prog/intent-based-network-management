class RoleManager:

    def __init__(self, roles, role_assignments):
        self.roles = roles
        self.role_assignments = role_assignments
        self.resolved_roles = {}

    def resolve_roles(self):
        self.resolved_roles = {}

        for identity, assignment in self.role_assignments.items():
            role_name = assignment.get("role")

            if role_name not in self.roles:
                raise ValueError(
                    f"Identity '{identity}' references unknown role "
                    f"'{role_name}'."
                )

            policy = self.roles[role_name]
            vlan = policy.get("vlan")

            if vlan is None:
                raise ValueError(
                    f"Role '{role_name}' does not define a VLAN."
                )

            if not isinstance(vlan, int) or not 1 <= vlan <= 4094:
                raise ValueError(
                    f"Role '{role_name}' has an invalid VLAN '{vlan}'."
                )

            self.resolved_roles[identity] = {
                "role": role_name,
                "vlan": vlan,
                "priority": policy.get("priority"),
                "policy": policy,
            }

        return self.resolved_roles

    def display_assignments(self):
        print("\nRole Assignment Resolution")
        print("--------------------------")

        for identity, data in self.resolved_roles.items():
            print(
                f"{identity} -> {data['role']} "
                f"(VLAN: {data['vlan']}, "
                f"priority: {data['priority']})"
            )


def resolve_role_assignments(intent):
    roles = intent.get("roles", {})
    role_assignments = intent.get("role_assignments", {})

    manager = RoleManager(roles, role_assignments)
    resolved_roles = manager.resolve_roles()
    manager.display_assignments()

    return resolved_roles


if __name__ == "__main__":
    print("RoleManager module loaded successfully.")

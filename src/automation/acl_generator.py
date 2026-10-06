class ACLGenerator:

    RESOURCE_FIELDS = {
        "internet": "INTERNET",
        "academic_resources": "ACADEMIC_RESOURCES",
        "internal_network": "INTERNAL_NETWORK",
        "student_network": "STUDENT_NETWORK",
        "teacher_network": "TEACHER_NETWORK",
    }

    def __init__(self, roles):
        self.roles = roles

    def generate(self):
        acl_policies = {}

        for role_name, policy in self.roles.items():
            rules = []

            for field, resource_name in self.RESOURCE_FIELDS.items():
                access = "ALLOW" if policy.get(field) is True else "DENY"

                rules.append({
                    "resource": resource_name,
                    "access": access,
                })

            acl_policies[role_name] = {
                "vlan": policy.get("vlan"),
                "priority": policy.get("priority"),
                "rules": rules,
            }

        return acl_policies

    def display(self, acl_policies):
        print("\nRole-Based ACL Policies")
        print("-----------------------")

        for role, policy in acl_policies.items():
            print(
                f"\n{role.upper()} "
                f"(VLAN {policy['vlan']}, "
                f"priority: {policy['priority']})"
            )

            for rule in policy["rules"]:
                print(
                    f"  {rule['resource']}: "
                    f"{rule['access']}"
                )


def generate_acl_policies(intent):
    roles = intent.get("roles", {})

    generator = ACLGenerator(roles)
    acl_policies = generator.generate()
    generator.display(acl_policies)

    return acl_policies


if __name__ == "__main__":
    print("ACLGenerator module loaded successfully.")

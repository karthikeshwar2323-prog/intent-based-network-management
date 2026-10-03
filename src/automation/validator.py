from intent.intent_parser import load_intent


def validate_intent(intent):
    errors = []

    # Validate intent information
    if not intent.get("intent", {}).get("name"):
        errors.append("Intent name is missing.")

    if not intent.get("intent", {}).get("description"):
        errors.append("Intent description is missing.")

    # Validate campus information
    if not intent.get("campus", {}).get("name"):
        errors.append("Campus name is missing.")

    # Validate network information
    network = intent.get("network", {})

    if network.get("management_protocol") != "netconf":
        errors.append("Management protocol must be NETCONF.")

    if network.get("device_type") != "cisco_ios_xe":
        errors.append("Device type must be cisco_ios_xe.")

    # Validate required roles
    roles = intent.get("roles", {})
    required_roles = ["teachers", "students", "guests"]

    for role in required_roles:
        if role not in roles:
            errors.append(f"Required role is missing: {role}")

    # Validate role policies
    valid_priorities = ["high", "normal", "low"]

    for role in required_roles:
        if role not in roles:
            continue

        policy = roles[role]

        required_fields = [
            "internet",
            "academic_resources",
            "internal_network",
            "student_network",
            "teacher_network",
            "priority"
        ]

        for field in required_fields:
            if field not in policy:
                errors.append(
                    f"{role} policy is missing field: {field}"
                )

        if "priority" in policy:
            if policy["priority"] not in valid_priorities:
                errors.append(
                    f"{role} has invalid priority: "
                    f"{policy['priority']}"
                )

        boolean_fields = [
            "internet",
            "academic_resources",
            "internal_network",
            "student_network",
            "teacher_network"
        ]

        for field in boolean_fields:
            if field in policy and not isinstance(policy[field], bool):
                errors.append(
                    f"{role}.{field} must be true or false."
                )

    # Validate interface policy
    policies = intent.get("policies", {})
    interface = policies.get("interface", {})

    if not interface.get("name"):
        errors.append("Interface name is missing.")

    if not interface.get("description"):
        errors.append("Interface description is missing.")

    if errors:
        print("Intent validation FAILED")

        for error in errors:
            print("-", error)

        return False

    print("Intent validation PASSED")
    return True


if __name__ == "__main__":
    intent = load_intent("config/intent.yaml")
    validate_intent(intent)

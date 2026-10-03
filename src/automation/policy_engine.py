def detect_conflicts(intent):
    conflicts = []

    roles = intent.get("roles", {})

    # Check that required roles exist
    required_roles = ["teachers", "students", "guests"]

    for role in required_roles:
        if role not in roles:
            conflicts.append(f"Missing required role: {role}")

    if conflicts:
        print("POLICY CONFLICTS DETECTED")

        for conflict in conflicts:
            print("-", conflict)

        return False

    print("Policy conflict check PASSED")
    return True

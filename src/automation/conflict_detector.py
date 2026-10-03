class ConflictDetector:

    VALID_PRIORITIES = ["high", "normal", "low"]

    def __init__(self, policies):
        self.policies = policies
        self.conflicts = []

    def check_priority_conflicts(self):
        """Check whether every role has a valid priority."""

        for role_name, policy in self.policies.items():

            priority = policy.get("priority")

            if priority not in self.VALID_PRIORITIES:

                self.conflicts.append(
                    f"{role_name}: invalid priority '{priority}'."
                )

    def check_role_access_conflicts(self):
        """Check for contradictory role access rules."""

        for role_name, policy in self.policies.items():

            # A role should not have both student and teacher
            # network access at the same time.
            student_access = policy.get(
                "student_network_access"
            )

            teacher_access = policy.get(
                "teacher_network_access"
            )

            if (
                student_access == "ALLOW"
                and teacher_access == "ALLOW"
            ):

                self.conflicts.append(
                    f"{role_name}: cannot allow both "
                    "student and teacher network access."
                )

    def check_role_priority_conflicts(self):
        """Check whether the intended role priorities are consistent."""

        expected_priorities = {
            "teachers": "high",
            "students": "normal",
            "guests": "low",
        }

        for role_name, expected_priority in expected_priorities.items():

            if role_name not in self.policies:
                continue

            actual_priority = self.policies[role_name].get(
                "priority"
            )

            if actual_priority != expected_priority:

                self.conflicts.append(
                    f"{role_name}: expected priority "
                    f"'{expected_priority}' but found "
                    f"'{actual_priority}'."
                )

    def check(self):
        """Run all policy conflict checks."""

        self.conflicts = []

        self.check_priority_conflicts()
        self.check_role_access_conflicts()
        self.check_role_priority_conflicts()

        if self.conflicts:

            print("\nPolicy Conflict Detection FAILED")
            print("--------------------------------")

            for conflict in self.conflicts:
                print("CONFLICT:", conflict)

            return False

        print("\nPolicy Conflict Detection PASSED")
        print("--------------------------------")
        print("No policy conflicts detected.")

        return True


if __name__ == "__main__":

    print("ConflictDetector module loaded successfully.")

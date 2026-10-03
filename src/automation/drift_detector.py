from intent.intent_parser import load_intent
from automation.verifier import get_actual_configuration


class DriftDetector:

    def __init__(self, expected_configuration, actual_configuration):
        self.expected_configuration = expected_configuration
        self.actual_configuration = actual_configuration
        self.drift_items = []

    def check_interface_description(self):
        """Compare expected and actual interface description."""

        expected = self.expected_configuration.get(
            "interface_description"
        )

        actual = self.actual_configuration.get(
            "interface_description"
        )

        if expected != actual:
            self.drift_items.append(
                "Interface description drift detected: "
                f"expected '{expected}', "
                f"but found '{actual}'."
            )

    def check(self):
        """Run all drift checks."""

        self.drift_items = []

        self.check_interface_description()

        if self.drift_items:
            print("\nDrift Detection FAILED")
            print("----------------------")

            for item in self.drift_items:
                print("DRIFT:", item)

            return False

        print("\nDrift Detection PASSED")
        print("---------------------")
        print("Actual configuration matches the intended configuration.")

        return True


def build_expected_configuration(intent):
    """Build the expected configuration from the campus intent."""

    interface = intent["policies"]["interface"]

    return {
        "interface_description": interface["description"]
    }


def load_expected_configuration():
    """Load expected configuration directly from intent.yaml."""

    intent = load_intent("config/intent.yaml")

    return build_expected_configuration(intent)


def get_live_drift_status(intent=None):
    """Compare intent configuration with the live Cisco configuration."""

    if intent is None:
        intent = load_intent("config/intent.yaml")

    expected_configuration = build_expected_configuration(intent)
    actual_configuration = get_actual_configuration(intent)

    detector = DriftDetector(
        expected_configuration,
        actual_configuration
    )

    return detector.check()


if __name__ == "__main__":

    print("Checking live Cisco configuration for drift...")

    get_live_drift_status()

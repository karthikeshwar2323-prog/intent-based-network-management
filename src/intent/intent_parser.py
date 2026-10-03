import yaml


def load_intent(file_path):
    """
    Load the complete network intent from a YAML file.
    """

    with open(file_path, "r") as file:
        intent = yaml.safe_load(file)

    return intent


if __name__ == "__main__":
    intent = load_intent("config/intent.yaml")

    print("Intent-Based Network Management")
    print("--------------------------------")

    print("Intent Name:", intent["intent"]["name"])
    print("Description:", intent["intent"]["description"])

    print("Campus:", intent["campus"]["name"])

    print("Management Protocol:",
          intent["network"]["management_protocol"])

    print("Device Type:",
          intent["network"]["device_type"])

    print("\nRoles:")

    for role, policy in intent["roles"].items():
        print(f"\n{role.upper()}")
        print("  Internet:", policy["internet"])
        print("  Academic Resources:", policy["academic_resources"])
        print("  Internal Network:", policy["internal_network"])
        print("  Student Network:", policy["student_network"])
        print("  Teacher Network:", policy["teacher_network"])
        print("  Priority:", policy["priority"])

    print("\nInterface:",
          intent["policies"]["interface"]["name"])

    print("Interface Description:",
          intent["policies"]["interface"]["description"])

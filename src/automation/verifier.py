from ncclient import manager
from intent.intent_parser import load_intent


HOST = "10.10.20.48"
USERNAME = "developer"
PORT = 830


def get_actual_configuration(intent=None):

    if intent is None:
        intent = load_intent("config/intent.yaml")

    interface = intent["policies"]["interface"]

    interface_name = interface["name"]

    interface_type = "GigabitEthernet"

    if not interface_name.startswith(interface_type):
        raise ValueError(
            f"Unsupported interface format: {interface_name}"
        )

    interface_number = interface_name.replace(
        interface_type, "", 1
    )

    filter_xml = f"""<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <interface>
    <GigabitEthernet>
      <name>{interface_number}</name>
    </GigabitEthernet>
  </interface>
</native>"""

    print("Connecting to Cisco IOS-XE for configuration retrieval...")

    connection = manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=input("Enter NETCONF password: "),
        hostkey_verify=False,
        device_params={"name": "default"},
        timeout=30
    )

    try:
        result = connection.get_config(
            source="running",
            filter=("subtree", filter_xml)
        )
    finally:
        connection.close_session()

    xml = result.xml

    description_start = "<description>"
    description_end = "</description>"

    start_index = xml.find(description_start)

    if start_index == -1:
        actual_description = None
    else:
        start_index += len(description_start)
        end_index = xml.find(description_end, start_index)

        if end_index == -1:
            actual_description = None
        else:
            actual_description = xml[start_index:end_index]

    return {
        "interface_description": actual_description
    }


def verify_configuration(intent=None):

    if intent is None:
        intent = load_intent("config/intent.yaml")

    actual_configuration = get_actual_configuration(intent)

    expected_description = (
        intent["policies"]["interface"]["description"]
    )

    if (
        actual_configuration["interface_description"]
        == expected_description
    ):
        print("Verification PASSED")
        print(
            "Interface:",
            intent["policies"]["interface"]["name"]
        )
        print(
            "Description:",
            actual_configuration["interface_description"]
        )
        return True

    print("Verification FAILED")
    print("Expected description:", expected_description)
    print(
        "Actual description:",
        actual_configuration["interface_description"]
    )
    return False


if __name__ == "__main__":

    intent = load_intent("config/intent.yaml")

    actual = get_actual_configuration(intent)

    print("\nActual configuration:")
    print(actual)

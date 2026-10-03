from intent.intent_parser import load_intent


def generate_interface_config(intent):
    """
    Generate Cisco IOS-XE NETCONF XML from the interface intent.
    """

    interface = intent["policies"]["interface"]

    interface_name = interface["name"]
    description = interface["description"]

    interface_type = "GigabitEthernet"

    if not interface_name.startswith(interface_type):
        raise ValueError(
            f"Unsupported interface format: {interface_name}"
        )

    interface_number = interface_name.replace(
        interface_type, "", 1
    )

    enabled = interface.get("enabled", True)

    shutdown_config = ""

    if not enabled:
        shutdown_config = "\n        <shutdown/>"

    return f"""<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <interface>
    <GigabitEthernet>
      <name>{interface_number}</name>
      <description>{description}</description>{shutdown_config}
    </GigabitEthernet>
  </interface>
</native>"""


if __name__ == "__main__":
    intent = load_intent("config/intent.yaml")

    print("Generated Interface Configuration")
    print("---------------------------------")
    print(generate_interface_config(intent))

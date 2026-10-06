from intent.intent_parser import load_intent


class ConfigurationGenerator:

    def __init__(self, intent):
        self.intent = intent

    def generate_vlan_policy(self):
        """
        Generate role-to-VLAN mappings at the intent/policy layer.

        VLAN configuration is intentionally NOT included in the live
        NETCONF payload because the target IOS-XE routing platform
        explicitly marks the OpenConfig VLAN subtree as unsupported.
        """

        roles = self.intent.get("roles", {})

        vlan_policies = []

        for role_name, policy in roles.items():

            vlan_id = policy.get("vlan")

            if vlan_id is None:
                continue

            vlan_policies.append({
                "role": role_name,
                "vlan": vlan_id,
                "name": role_name.upper(),
                "priority": policy.get("priority"),
            })

        return vlan_policies

    def display_vlan_policy(self, vlan_policies):
        print("\nRole-Based VLAN Intent")
        print("----------------------")

        for policy in vlan_policies:
            print(
                f"{policy['role']} -> "
                f"VLAN {policy['vlan']} "
                f"({policy['name']}, "
                f"priority: {policy['priority']})"
            )

        print(
            "\nNote: VLAN configuration is retained as intent/policy "
            "because the target IOS-XE platform does not support "
            "the OpenConfig VLAN configuration subtree."
        )

    def generate_acls(self):
        """
        Generate role-based ACL policy definitions.

        ACL enforcement is not included in the live NETCONF payload
        because the current intent does not yet define concrete
        source/destination network addresses.
        """

        roles = self.intent.get("roles", {})

        acl_blocks = []

        for role_name, policy in roles.items():

            vlan_id = policy.get("vlan")

            if vlan_id is None:
                continue

            acl_name = f"{role_name.upper()}_ACL"

            acl_blocks.append(
                f"""    <!-- {acl_name} for VLAN {vlan_id} -->
    <!-- ACL policy generated at the intent layer -->
    <!-- Cisco ACE rules require concrete resource network definitions. -->"""
            )

        return "\n".join(acl_blocks)

    def generate_interface(self):
        """
        Generate the existing Cisco IOS-XE interface configuration
        from the interface intent.
        """

        interface = self.intent["policies"]["interface"]

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

        return f"""  <interface>
    <GigabitEthernet>
      <name>{interface_number}</name>
      <description>{description}</description>{shutdown_config}
    </GigabitEthernet>
  </interface>"""

    def generate(self):
        """
        Generate device-compatible configuration.

        Role/VLAN information remains part of the intent layer,
        but unsupported OpenConfig VLAN configuration is excluded
        from the live NETCONF payload.

        The existing Cisco IOS-XE native interface configuration
        remains deployable.
        """

        vlan_policy = self.generate_vlan_policy()
        self.display_vlan_policy(vlan_policy)

        acl_config = self.generate_acls()
        interface_config = self.generate_interface()

        return f"""<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">

  <!--
    Role-based VLAN intent is maintained by the policy layer.
    The target IOS-XE routing platform explicitly marks
    /openconfig-vlan:vlans as not-supported.
  -->

  <!-- Role-based ACL policy definitions -->
{acl_config}

  <!-- Cisco IOS-XE interface configuration -->
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
{interface_config}
  </native>

</config>"""


def generate_cisco_config(intent):
    """
    Generate complete device-compatible intent configuration.
    """

    generator = ConfigurationGenerator(intent)

    return generator.generate()


def generate_interface_config(intent):
    """
    Backward-compatible wrapper for the existing workflow.
    """

    return generate_cisco_config(intent)


if __name__ == "__main__":

    intent = load_intent("config/intent.yaml")

    generator = ConfigurationGenerator(intent)

    print("Generated Intent-Based Cisco Configuration")
    print("--------------------------------------------")
    print(generate_cisco_config(intent))

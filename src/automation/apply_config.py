from ncclient import manager

from automation.config_generator import generate_interface_config
from automation.backup_config import backup_configuration
from automation.verifier import verify_configuration
from observability.metrics import (
    record_netconf_connection,
    record_deployment,
    record_verification,
)


HOST = "10.10.20.48"
USERNAME = "developer"
PORT = 830


def apply_configuration(intent):

    print("\nStep 6: Creating configuration backup...")
    backup_configuration()

    print("\nStep 7: Generating device-compatible configuration...")
    configuration = generate_interface_config(intent)

    print("\nGenerated NETCONF configuration:")
    print(configuration)

    print("\nStep 8: Connecting to Cisco IOS-XE...")

    try:
        connection = manager.connect(
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=input("Enter NETCONF password: "),
            hostkey_verify=False,
            device_params={"name": "default"},
            timeout=30
        )

        record_netconf_connection(True)

        print("NETCONF connection successful!")
        print("Session ID:", connection.session_id)

    except Exception as error:
        record_netconf_connection(False)
        record_deployment(False)

        print("\nNETCONF connection failed.")
        print("Error:", error)

        return False

    try:
        print("\nStep 9: Applying intent configuration...")

        result = connection.edit_config(
            target="running",
            config=configuration,
            default_operation="merge",
            error_option="rollback-on-error"
        )

        record_deployment(True)

        print("\nConfiguration result:")
        print(result.xml)

    except Exception as error:
        record_deployment(False)

        print("\nConfiguration deployment failed.")
        print("Error:", error)

        return False

    finally:
        connection.close_session()
        print("\nNETCONF session closed.")

    print("\nStep 10: Verifying configuration...")

    verification_result = verify_configuration(intent)

    record_verification(verification_result)

    if verification_result:
        print("\nIntent successfully applied and verified.")
        return True

    print("\nVerification failed.")
    return False


if __name__ == "__main__":
    from intent.intent_parser import load_intent

    intent = load_intent("config/intent.yaml")
    apply_configuration(intent)

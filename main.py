from observability.server import start_metrics_server
from observability.metrics import record_validation, record_configuration_generation, record_drift_check
from intent.intent_parser import load_intent
from automation.validator import validate_intent
from automation.policy_engine import detect_conflicts
from automation.role_manager import resolve_role_assignments
from automation.acl_generator import generate_acl_policies
from automation.config_generator import generate_interface_config
from automation.apply_config import apply_configuration
from automation.audit_logger import AuditLogger
from automation.drift_detector import load_expected_configuration


def main():
    start_metrics_server(8000)

    print("=" * 60)
    print(" ROLE-BASED INTENT NETWORK MANAGEMENT SYSTEM")
    print("=" * 60)

    intent = load_intent("config/intent.yaml")

    intent_name = intent["intent"]["name"]
    campus_name = intent["campus"]["name"]
    roles = list(intent["roles"].keys())

    logger = AuditLogger()

    # Step 1: Load campus intent
    print("\nStep 1: Loading campus network intent...")

    print("Intent:", intent_name)
    print("Campus:", campus_name)
    print("Device Type:", intent["network"]["device_type"])
    print(
        "Management Protocol:",
        intent["network"]["management_protocol"]
    )

    # Step 2: Validate intent
    print("\nStep 2: Validating campus intent...")

    validation_result = validate_intent(intent)
    record_validation(validation_result)

    if not validation_result:

        logger.log_event(
            intent_name=intent_name,
            campus_name=campus_name,
            execution_mode="precheck",
            result="FAILED",
            message="Intent validation failed.",
            roles=roles
        )

        print("\nWorkflow stopped because intent validation failed.")
        return

    # Step 3: Resolve role assignments
    print("\nStep 3: Resolving role assignments...")

    resolved_roles = resolve_role_assignments(intent)

    # Step 4: Detect policy conflicts
    print("\nStep 4: Checking for policy conflicts...")

    if not detect_conflicts(intent):

        logger.log_event(
            intent_name=intent_name,
            campus_name=campus_name,
            execution_mode="precheck",
            result="FAILED",
            message="Policy conflicts were detected.",
            roles=roles
        )

        print(
            "\nWorkflow stopped because policy conflicts were detected."
        )
        return

    # Step 5: Display role policies
    print("\nStep 5: Role-based policies loaded...")

    for role, policy in intent["roles"].items():

        print(f"\n{role.upper()}")
        print("  Internet:", policy["internet"])
        print(
            "  Academic Resources:",
            policy["academic_resources"]
        )
        print(
            "  Internal Network:",
            policy["internal_network"]
        )
        print(
            "  Student Network:",
            policy["student_network"]
        )
        print(
            "  Teacher Network:",
            policy["teacher_network"]
        )
        print("  Priority:", policy["priority"])

    # Step 6: Generate role-based ACL policies
    print("\nStep 6: Generating role-based ACL policies...")

    acl_policies = generate_acl_policies(intent)

    # Step 7: Generate Cisco configuration
    print("\nStep 7: Generating Cisco IOS-XE NETCONF XML...")

    native_config = generate_interface_config(intent)
    record_configuration_generation()

    print("\nGenerated Configuration:")
    print(native_config)

    # Step 8: Load expected configuration
    print("\nStep 8: Loading expected configuration...")

    expected_configuration = load_expected_configuration()

    print("Expected configuration:")
    print(expected_configuration)

    # Step 9: Select execution mode
    print("\n" + "=" * 60)
    print(" EXECUTION MODE")
    print("=" * 60)

    print("\n1. Simulation Mode")
    print("2. Live Cisco NETCONF Mode")

    choice = input("\nSelect mode (1/2): ").strip()

    # Step 10: Simulation
    if choice == "1":

        print("\nSimulation Mode selected.")
        print("Configuration was NOT sent to Cisco.")
        print("Live drift detection was NOT performed.")

        logger.log_event(
            intent_name=intent_name,
            campus_name=campus_name,
            execution_mode="simulation",
            result="SUCCESS",
            message=(
                "Role-based intent processed and "
                "configuration generated successfully. "
                "Live drift detection was not performed."
            ),
            roles=roles
        )

    # Step 11: Live deployment
    elif choice == "2":

        print("\nLive Cisco NETCONF Mode selected.")

        success = apply_configuration(intent)

        if not success:

            logger.log_event(
                intent_name=intent_name,
                campus_name=campus_name,
                execution_mode="live_netconf",
                result="FAILED",
                message=(
                    "Configuration deployment or verification "
                    "failed."
                ),
                roles=roles
            )

            print(
                "\nLive deployment did not complete successfully."
            )
            return

        print("\nStep 12: Checking live Cisco configuration for drift...")

        from automation.drift_detector import get_live_drift_status

        drift_free = get_live_drift_status(intent)
        record_drift_check(drift_free)

        if drift_free:

            logger.log_event(
                intent_name=intent_name,
                campus_name=campus_name,
                execution_mode="live_netconf",
                result="SUCCESS",
                message=(
                    "Intent configuration was applied, verified, "
                    "and live drift detection passed."
                ),
                roles=roles
            )

        else:

            logger.log_event(
                intent_name=intent_name,
                campus_name=campus_name,
                execution_mode="live_netconf",
                result="DRIFT_DETECTED",
                message=(
                    "Intent configuration was applied and verified, "
                    "but live drift detection detected a difference."
                ),
                roles=roles
            )

            print(
                "\nLive configuration differs from the intended "
                "configuration."
            )
            return

    # Invalid execution mode
    else:

        print("\nInvalid execution mode.")

        logger.log_event(
            intent_name=intent_name,
            campus_name=campus_name,
            execution_mode="unknown",
            result="FAILED",
            message="Invalid execution mode selected.",
            roles=roles
        )

        return

    print("\n" + "=" * 60)
    print(" WORKFLOW FINISHED")
    print("=" * 60)

    print("\nPrometheus metrics server is running on port 8000.")
    print("Press Ctrl+C to stop the application.")

    try:
        while True:
            input()
    except KeyboardInterrupt:
        print("\nApplication stopped.")


if __name__ == "__main__":
    main()

from datetime import datetime
from pathlib import Path
import json


class AuditLogger:

    def __init__(self, log_directory="audit_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)

    def log_event(
        self,
        intent_name,
        campus_name,
        execution_mode,
        result,
        message,
        roles=None
    ):
        """Record an automation event in a JSON audit log."""

        timestamp = datetime.now()

        event = {
            "timestamp": timestamp.isoformat(),
            "intent_name": intent_name,
            "campus_name": campus_name,
            "execution_mode": execution_mode,
            "result": result,
            "message": message,
            "roles": roles or []
        }

        filename = (
            f"audit_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
        )

        log_file = self.log_directory / filename

        with open(log_file, "w") as file:
            json.dump(event, file, indent=4)

        print("\nAudit log created:")
        print(log_file)

        return log_file


if __name__ == "__main__":

    logger = AuditLogger()

    logger.log_event(
        intent_name="campus_role_based",
        campus_name="REVA University",
        execution_mode="simulation",
        result="SUCCESS",
        message="Role-based intent processed successfully.",
        roles=["teachers", "students", "guests"]
    )

from ncclient import manager
from datetime import datetime
from pathlib import Path


HOST = "10.10.20.48"
USERNAME = "developer"
PORT = 830


def backup_configuration():
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    print("Connecting to Cisco IOS-XE...")

    connection = manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=input("Enter NETCONF password: "),
        hostkey_verify=False,
        device_params={"name": "default"},
        timeout=30
    )

    print("NETCONF connection successful!")

    running_config = connection.get_config(source="running").xml

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"running_config_{timestamp}.xml"

    backup_file.write_text(running_config)

    print("Configuration backup created:")
    print(backup_file)

    connection.close_session()
    print("NETCONF session closed.")


if __name__ == "__main__":
    backup_configuration()

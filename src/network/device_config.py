import yaml


class DeviceConfig:

    def __init__(self, file_path="config/devices.yaml"):
        self.file_path = file_path
        self.devices = {}

        self.load_devices()

    def load_devices(self):
        """Load network device configuration from YAML."""

        with open(self.file_path, "r") as file:
            data = yaml.safe_load(file)

        device_list = data.get("devices", [])

        for device in device_list:

            name = device.get("name")

            if not name:
                continue

            self.devices[name] = device

    def get_device(self, name="campus-router"):
        """Return configuration for a specific network device."""

        if name not in self.devices:
            raise ValueError(
                f"Device '{name}' was not found in devices.yaml."
            )

        return self.devices[name]

    def validate_device(self, device):
        """Validate required device configuration fields."""

        required_fields = [
            "name",
            "host",
            "username",
            "port",
            "protocol",
        ]

        for field in required_fields:

            if field not in device:
                raise ValueError(
                    f"Device configuration is missing: {field}"
                )

        if device["protocol"] != "netconf":
            raise ValueError(
                "Device protocol must be NETCONF."
            )

        if not isinstance(device["port"], int):
            raise ValueError(
                "Device port must be an integer."
            )

        return True


if __name__ == "__main__":

    config = DeviceConfig()

    device = config.get_device()

    config.validate_device(device)

    print("\nDevice Configuration")
    print("--------------------")
    print("Name:", device["name"])
    print("Host:", device["host"])
    print("Username:", device["username"])
    print("Port:", device["port"])
    print("Protocol:", device["protocol"])

    print("\nDevice configuration validation PASSED.")

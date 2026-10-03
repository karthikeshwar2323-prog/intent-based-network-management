from ncclient import manager

HOST = "10.10.20.48"
USERNAME = "developer"
PORT = 830

def connect_to_device():
    print("Connecting to Cisco IOS-XE device...")

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
    print("Session ID:", connection.session_id)

    print("\nReading running configuration...")
    config = connection.get_config(source="running")

    print(config.xml[:5000])

    connection.close_session()
    print("\nNETCONF session closed.")

if __name__ == "__main__":
    connect_to_device()

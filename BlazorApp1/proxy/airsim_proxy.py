from os import path
import string
import airsim
import socket
import threading

# Initialize AirSim client
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# UDP Server Setup
UDP_IP = "172.26.112.1"
UDP_COMMAND_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_COMMAND_PORT))
print(f"Proxy listening on {UDP_IP}:{UDP_COMMAND_PORT}")


def startFixedPath(path):
    print(f"Executing Fixed Flight Path: {path}")

    client.enableApiControl(True)
    client.armDisarm(True)
    client.takeoffAsync().join()
    state = client.getMultirotorState()

    while state.landed_state == airsim.LandedState.Landed:
        print("keep trying to take off")
        client.armDisarm(True)
        client.takeoffAsync().join()
        state = client.getMultirotorState()  # Update state
    s = -10
    print("make sure we are hovering at {} meters...".format(-s))
    client.moveToZAsync(s, 10).join()  # Changed to 10 m/s

    if path == "FixedPath1":
        client.moveOnPathAsync([airsim.Vector3r(125,0,s),
                           airsim.Vector3r(125,-130,s),
                           airsim.Vector3r(0,-130,s),
                           airsim.Vector3r(0,0,s)],
                            10, 120, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), 20, 1).join()
        client.moveToPositionAsync(0,0,s,10).join()  # Changed to 10 m/s
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        print("✅ Fixed Flight Path Completed!")
    elif path == "FixedPath2":
        client.moveOnPathAsync([airsim.Vector3r(0,0,s), airsim.Vector3r(100,-100,s), airsim.Vector3r(-100,-100,s), airsim.Vector3r(0,0,s)], 10, 120, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), 20, 1).join()
        client.moveToPositionAsync(0,0,s,10).join()  # Changed to 10 m/s
        client.moveToPositionAsync(0,0,s,1).join()
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        print("✅ Fixed Flight Path Completed!")    
    else:
        print(f"⚠️ Unknown path: {path}")


def execute_command(command):
    print(f"execute_command() called with: {command}")
    z = client.getMultirotorState().kinematics_estimated.position.z_val
    state = client.getMultirotorState()
    if command == "armNtakeoff":
        while state.landed_state == airsim.LandedState.Landed:
            print("keep trying to take off")
            client.armDisarm(True)
            client.takeoffAsync().join()
            state = client.getMultirotorState()  # Update state
    elif command == "landNdisarm":
        while state.landed_state != airsim.LandedState.Landed:
            print("keep trying to land")
            client.landAsync().join()
            client.armDisarm(False)
            state = client.getMultirotorState()  # Update state
    elif command == "return_home":
        client.goHomeAsync().join()
    elif command == "forward":
        client.moveByVelocityZAsync(2, 0, z, 1).join()
    elif command == "backward":
        client.moveByVelocityZAsync(-2, 0, z, 1).join()
    elif command == "left":
        client.moveByVelocityZAsync(0, -2, z, 1).join()
    elif command == "right":
        client.moveByVelocityZAsync(0, 2, z, 1).join()
    elif command == "stop":
        client.hoverAsync().join()
        client.landAsync().join()
        client.armDisarm(False)
    elif command in ["FixedPath1", "FixedPath2", "FixedPath3", "FixedPath4"]:
        startFixedPath(command)  # No need to assign 'path' globally
    else:
        print(f"⚠️ Unknown command: {command}")

while True:
    data, addr = sock.recvfrom(1024)
    command = data.decode().strip()
    threading.Thread(target=execute_command, args=(command,)).start()

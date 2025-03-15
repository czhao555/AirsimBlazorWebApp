from contextlib import nullcontext
from tarfile import NUL
import airsim
import socket
import threading
import time
import cv2
import numpy as np

# AirSim clients
video_client = airsim.MultirotorClient()
data_client = airsim.MultirotorClient()
video_client.confirmConnection()
data_client.confirmConnection()

# UDP settings
UDP_IP = "172.26.112.1"
UDP_VIDEO_PORT = 5001
UDP_DATA_PORT = 5002
UDP_REQUEST_PORT = 5003

# Create UDP sockets
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
request_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
request_sock.bind((UDP_IP, UDP_REQUEST_PORT))

MAX_UDP_PACKET_SIZE = 65000
FRAME_QUALITY = 40

print(f"Streaming video on {UDP_IP}:{UDP_VIDEO_PORT}")
print(f"Sending drone data on {UDP_IP}:{UDP_DATA_PORT}")
print(f"Listening for data requests on {UDP_IP}:{UDP_REQUEST_PORT}")

def send_video_stream():
    """Captures images from AirSim and sends them via UDP"""
    while True:
        try:
            response = video_client.simGetImage("0", airsim.ImageType.Scene)

            if response is None or len(response) == 0:
                print("[ERROR] Failed to get image!")
                continue

            img = np.frombuffer(response, dtype=np.uint8)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)

            if img is None:
                print("[ERROR] Failed to decode image!")
                continue

            img = cv2.resize(img, (640, 360))
            _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, FRAME_QUALITY])

            if buffer is None or len(buffer) == 0:
                print("[ERROR] Image encoding failed!")
                continue

            if len(buffer) > MAX_UDP_PACKET_SIZE:
                print(f"[ERROR] Frame too large ({len(buffer)} bytes). Lowering quality.")
                continue

            video_sock.sendto(buffer.tobytes(), (UDP_IP, UDP_VIDEO_PORT))
            print(f"[DEBUG] Video frame sent! Size: {len(buffer)} bytes")

        except Exception as e:
            print(f"[ERROR] Video stream error: {e}")

        time.sleep(0.1)

def get_drone_data():
    """Fetches drone telemetry data"""
    try:
        gps = data_client.getGpsData().gnss.geo_point
        velocity = data_client.getMultirotorState().kinematics_estimated.linear_velocity
        drone_state = data_client.getMultirotorState()
        collision_info = data_client.simGetCollisionInfo()

        # Calculate speed from velocity components (magnitude of the vector)
        speed = max(0, (velocity.x_val**2 + velocity.y_val**2 + velocity.z_val**2) ** 0.5)

        # Placeholder battery percentage
        battery= 85

        # Determine drone arming status
        armed = "Armed" if drone_state.landed_state == airsim.LandedState.Flying else "Disarmed"

        # Determine flight status
        if drone_state.landed_state == airsim.LandedState.Landed:
            flight_status = "Landed"
        else:
            flight_status = "Flying"

         # **Collision Detection**
        collision_count=0
        if collision_info.has_collided:
            collision_count += 1
            print(f"🚨 Collision #{collision_count} detected! Object: {collision_info.object_name}")
        else:
            print("❌ No Collision Detected!")


        gps_str = f"{gps.latitude:.6f},{gps.longitude:.6f},{gps.altitude:.2f}"
        speed_str = f"{speed:.2f}"
        battery_str = f"{battery}"
        drone_status_str = f"{armed}"
        flight_status_str = f"{flight_status}"
        collision_status_str = f"{collision_count}"

        return f"{gps_str},{speed_str},{battery_str},{drone_status_str},{flight_status_str},{collision_count}"
    except Exception as e:
        print(f"[ERROR] Failed to get drone data: {e}")
        return "0.0,0.0,0.0,0.0,0,Unknown,Unknown"


def send_drone_data():
    """Continuously sends drone data via UDP"""
    while True:
        data = get_drone_data()
        data_sock.sendto(data.encode(), (UDP_IP, UDP_DATA_PORT))
        print(f"[DEBUG] Drone data sent: {data}")
        time.sleep(1)

def listen_for_requests():
    """Listens for requests from Blazor and responds with drone data"""
    while True:
        try:
            request, addr = request_sock.recvfrom(1024)
            if request.decode() == "get_data":
                data = get_drone_data()
                data_sock.sendto(data.encode(), addr)
                print(f"[DEBUG] Responded to request with data: {data}")
        except Exception as e:
            print(f"[ERROR] Data request error: {e}")

# Start threads
threading.Thread(target=send_video_stream, daemon=True).start()
threading.Thread(target=send_drone_data, daemon=True).start()
threading.Thread(target=listen_for_requests, daemon=True).start()

while True:
    time.sleep(1)

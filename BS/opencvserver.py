import cv2
import socket
import pickle
import os
from datetime import datetime

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = "0.0.0.0"
server_port = 6666
s.bind((server_ip, server_port))

# Get parent directory path and logs folder
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Create unique filename with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
video_path = os.path.join(logs_dir, f"{timestamp}.mp4")

out = None

while True:
    x = s.recvfrom(1000000)
    client_ip = x[1][0]
    data = x[0]
    data = pickle.loads(data)

    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if img is None:
        continue

    if out is None:
        height, width, _ = img.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (width, height))

    out.write(img)
    cv2.imshow("Img Server", img)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

if out:
    out.release()
cv2.destroyAllWindows()

print(f"Video saved at: {video_path}")
# mac_udp_display.py
import socket
import pickle
import cv2
import numpy as np

# Bind to all interfaces
server_ip = ""
server_port = 6666
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((server_ip, server_port))
print(f"Listening on {server_ip}:{server_port}")

# Chunk reconstruction
HEADER_SIZE = 10
current_frame_chunk = []

while True:
    packet, addr = s.recvfrom(1500)
    if len(packet) < HEADER_SIZE:
        continue

    header = packet[:HEADER_SIZE].decode()
    try:
        chunk_num, total_chunks = map(int, header.split("/"))
    except:
        continue

    if chunk_num == 0:
        current_frame_chunk = [None] * total_chunks

    current_frame_chunk[chunk_num] = packet[HEADER_SIZE:]

    # If all chunks received, reconstruct frame
    if all(chunk is not None for chunk in current_frame_chunk):
        full_data = b"".join(current_frame_chunk)
        try:
            buffer = pickle.loads(full_data)
            img_array = np.frombuffer(buffer, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is not None:
                cv2.imshow("Received Video", img)

        except Exception as e:
            print(f"Failed to decode frame: {e}")

        # Reset for next frame
        current_frame_chunk = []

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
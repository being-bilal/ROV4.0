"""
QR Code Scanner
1. The video is read frame-by-frame using OpenCV.
2. Each frame undergoes preprocessing (white balance and contrast enhancement)
   to improve QR readability in underwater conditions.
3. QR detection is activated and deactivated manually using keyboard controls:
   - Press 's' to START QR recording
   - Press 'e' to END QR recording and finalize the decision
   - Press 'q' to quit the program
4. While recording is active, QR codes are detected in every frame using pyzbar.
5. QR codes detected in each frame are tallied to determine the most frequently
   detected QR code as the final decision.
6. Instructions list is stored containing all finalized QR code decisions.
"""


import cv2
from collections import Counter
from pyzbar import pyzbar
from preprocessing import white_balance, contrast_enhancement

window_name = 'QR Code Scanner'
video_path = 'recording2.mp4'

recording = False
detected_qrs = []
qr_votes = Counter()
final_decision = None
instruction_list = list()

print("Press 's' to START Detection ")
print("Press 'e' to END Detection")
print("Press 'q' to QUIT")

cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

total_frames = 0
qr_detected_frames = 0

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or cannot fetch the frame.")
        break

    display_frame = white_balance(frame.copy())
    display_frame = contrast_enhancement(display_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        recording = True
        print("QR Detection STARTED")
        detected_qrs.clear()
        qr_votes.clear()
        final_decision = None

    elif key == ord('e'):
        print("QR Detection ENDED")
        recording = False
        if qr_votes:
            final_decision = qr_votes.most_common(1)[0][0]
            instruction_list.append(final_decision)
            print("FINAL DECISION:", final_decision)
        else:
            pass
        
    elif key == ord('q'):
        print("Quitting.")
        break

    if recording:
        total_frames += 1
        qrs = pyzbar.decode(display_frame)
        frame_qrs = set()

        if qrs:
            qr_detected_frames += 1

            for qr in qrs:
                qr_data = qr.data.decode('utf-8')
                frame_qrs.add(qr_data)

                (x, y, w, h) = qr.rect
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(display_frame, qr_data, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            for qr_data in frame_qrs:
                detected_qrs.append(qr_data)
                qr_votes[qr_data] += 1

        if qr_votes:
            final_decision = qr_votes.most_common(1)[0][0]
            cv2.putText(display_frame, f"Final Decision: {final_decision}",
                        (10, height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow(window_name, display_frame)  
    out.write(display_frame)               

cap.release()
out.release()
cv2.destroyAllWindows()

print("Total frames processed:", total_frames)
print("Frames with QR code detected:", qr_detected_frames)
print("Detection Rate: {:.2f}%".format(
    (qr_detected_frames / total_frames) * 100 if total_frames > 0 else 0
))
print("Instructions List:", instruction_list)

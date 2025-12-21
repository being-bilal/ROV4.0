import cv2
from preprocessing import white_balance, contrast_enhancement

window_name = 'OpenCV QR Code'

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture('recording2.mp4')

total_frames = 0
qr_detected_frames = 0


while True:
    ret, frame = cap.read()
     
    if not ret:
        print("End of video or cannot fetch the frame.")
        break
    
    else:
        total_frames += 1
        frame = white_balance(frame)
        frame = contrast_enhancement(frame)
        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        if ret_qr == True:
            qr_detected_frames += 1
            for s, p in zip(decoded_info, points):
                if s != '':
                    # Draw the bounding box
                    color = (0, 255, 0)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
                    text_x = int(min(p[:, 0]))
                    text_y = int(max(p[:, 1]) + 30)
                    cv2.putText(frame,s,(text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0, 255, 0),2,cv2.LINE_AA)
                    
        cv2.imshow(window_name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)
cap.release()

print("Total frames processed:", total_frames)
print("Frames with QR code detected:", qr_detected_frames)
print("Detection Rate: {:.2f}%".format((qr_detected_frames / total_frames) * 100))
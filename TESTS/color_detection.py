import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 20, 20])
    upper_green = np.array([80, 255, 255])
    
    lower_red1 = np.array([0, 160, 20])
    upper_red1 = np.array([10, 255, 255])
    
    lower_red2 = np.array([160, 150, 20])
    upper_red2 = np.array([180, 255, 255])
    contour_area_threshold = 2000
    
    red_mask = cv2.bitwise_or(cv2.inRange(hsv_frame, lower_red1, upper_red1),
                            cv2.inRange(hsv_frame, lower_red2, upper_red2))
    green_mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    kernel = np.ones((7, 7), np.uint8)
    masks = [green_mask, red_mask]
    for i in range(len(masks)):
        masks[i] = cv2.morphologyEx(masks[i], cv2.MORPH_OPEN, kernel)
        masks[i] = cv2.morphologyEx(masks[i], cv2.MORPH_CLOSE, kernel)
        #masks[i] = cv2.erode(masks[i], kernel, iterations=1)
        #masks[i] = cv2.dilate(masks[i], kernel, iterations=1)

    combined_result = cv2.bitwise_or(
        cv2.bitwise_and(frame, frame, mask=green_mask),
        cv2.bitwise_and(frame, frame, mask=red_mask)
        )
    color_info = [
        ("Red", red_mask, (0, 0, 255)),
        ("Green", green_mask, (0, 255, 0))
    ]

    for name, mask, bgr in color_info:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > contour_area_threshold:  
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, 4)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, bgr, 2)

   
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Detected Colors", combined_result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
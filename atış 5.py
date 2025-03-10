import cv2
import numpy as np
import time


cv2.setUseOptimized(True)  
cv2.setNumThreads(4)  

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

shot_count = 10
auto_mode = False
last_shot_time = 0
manual_shot = False
hit_position = None
hit_time = 0
target_lost = False
stopped = False
reloading = False
reload_start_time = 0

def toggle_mode(event, x, y, flags, param):
    global auto_mode, manual_shot, stopped, reloading, reload_start_time, shot_count
    if event == cv2.EVENT_LBUTTONDOWN:
        if 10 < x < 110 and 10 < y < 60:
            auto_mode = not auto_mode
            manual_shot = False  
            stopped = False 
        elif 10 < x < 110 and 70 < y < 120:
            manual_shot = True
            auto_mode = False  
            stopped = False  
        elif 10 < x < 110 and 130 < y < 180:
            stopped = True 
            auto_mode = False
            manual_shot = False  
        elif 10 < x < 110 and 190 < y < 240:
            if not reloading:
                reloading = True
                reload_start_time = time.time()

cv2.namedWindow("Kamera")
cv2.setMouseCallback("Kamera", toggle_mode)

kernel = np.ones((3, 3), np.uint8) 

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.GaussianBlur(frame, (5, 5), 0)  
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 150, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 150, 100])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)  
    
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
    target_detected = False
    target_position = None
    
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Kirmizi Nesne", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            target_detected = True
            target_position = (x + w // 2, y + h // 2)
    
    current_time = time.time()
    
    if reloading:
        remaining_time = 5 - (current_time - reload_start_time)
        if remaining_time <= 0:
            shot_count = 10
            reloading = False
        else:
            cv2.putText(frame, f"Reloading: {int(remaining_time)}s", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    if not stopped and not reloading:
        if auto_mode and target_detected and shot_count > 0:
            if current_time - last_shot_time >= 1.5:
                print("Otonom Atis yapildi ")
                shot_count -= 1
                last_shot_time = current_time
                hit_position = target_position
                hit_time = current_time
                target_lost = False
    
        if manual_shot:
            if shot_count > 0:
                if target_detected:
                    print("Manuel Atis Basarili Hedef Vuruldu ")
                    hit_position = target_position
                    hit_time = current_time
                else:
                    print("Manuel Atis Basarisiz Hedef Yok ")
                shot_count -= 1
            else:
                print("Atis hakki kalmadi ")
            manual_shot = False
    
    if hit_position and current_time - hit_time < 0.3:
        cv2.circle(frame, hit_position, 10, (255, 0, 0), -1)
    
    
    cv2.rectangle(frame, (10, 10), (110, 60), (255, 0, 0), 2)
    cv2.putText(frame, "Auto Mode", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.rectangle(frame, (10, 70), (110, 120), (0, 255, 0), 2)
    cv2.putText(frame, "Manual Shot", (15, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.rectangle(frame, (10, 130), (110, 180), (0, 0, 255), 2)
    cv2.putText(frame, "Stop", (15, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.rectangle(frame, (10, 190), (110, 240), (0, 255, 255), 2)
    cv2.putText(frame, "Reload", (15, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    
    cv2.putText(frame, f"Mermi: {shot_count}", (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Kamera", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

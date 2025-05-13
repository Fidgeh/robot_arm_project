import cv2
import mediapipe as mp
import serial
import time

# Anslut till Arduino med pySerial
arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)
time.sleep(2)  # Vänta lite för att säkerställa att anslutningen är upprättad

# Mediapipe-inställningar
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

            # Använd handledets position (handledet är vanligtvis index 0)
            wrist = lmList[0]
            x, y = wrist[1], wrist[2]  # X- och Y-position på handen

            # Mappa handens position till servo-vinklar (0–180)
            servo1_angle = int((1 - y / h) * 180)  # vertikal (omvänd y)
            servo2_angle = int((x / w) * 180)        # horisontell

            # Begränsa värdena mellan 0–180
            servo1_angle = max(0, min(180, servo1_angle))
            servo2_angle = max(0, min(180, servo2_angle))

            # Grepp (servo3) – baserat på avståndet mellan tumme (id 4) och pekfinger (id 8)
            thumb = lmList[4]
            index = lmList[8]
            distance = ((thumb[1] - index[1]) ** 2 + (thumb[2] - index[2]) ** 2) ** 0.5
            grip_angle = int(max(0, min(180, (1 - distance / 150) * 180)))

            # Skicka kommandon till Arduino via serial, t.ex. "9:angle"
            # Justera pin-numren om du använder andra kopplingar
            command1 = f"9:{servo1_angle}\n"
            command2 = f"10:{servo2_angle}\n"
            command3 = f"11:{grip_angle}\n"
            arduino.write(command1.encode())
            arduino.write(command2.encode())
            arduino.write(command3.encode())

            # Visualisering i OpenCV
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            cv2.putText(img, f"X:{servo2_angle} Y:{servo1_angle} Grip:{grip_angle}", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.imshow("Servo Control", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Avsluta med ESC
        break

cap.release()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import serial
import time

#====== cấu hình arduino========#
arduino_port = 'COM3'
baud_rate = 9600 # khop voi cong com Serial.begin(9600)

try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f" da ket noi duoc voi Arduino qua cong {arduino_port}")
    
    time.sleep(2) # delay cho arduino sau khi khoi dong
except Exception as e:
    # phat hien cam sai cong hoac chua cam mach
    print(f"khong the ket noi voi arduino:{e}")
    arduino = None

#=========khoi tao gia tri cho medipipe========#
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence = 0.7)

mp_draw = mp.solutions.drawing_utils # ve cac diem landmark

#======== dinh nghia cac diem tren ban tay
#ngoncai(4) ngontro(8) ngongiua(12) ngonaput(16) ngonut(20)
tipIds  = [4, 8, 12 , 16, 20]

current_command = -1 # chua co lenh nao

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("khong mo duoc camera")
    exit()

print(" bat dau nhan dien an q de thoat")

#===================vong lap xu ly hinh anh chinhs 
while True:
    #doc khung hinh tu cam (frame) tu webcam
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img,1) # lat nguoc camera

    # chuyen mau cho midiapipe
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks: #duyet qua 1 ban tay
            # ve 21 diem va cac duong noi tren ban tay
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            listx_y = []

            # lap qua 21 diem 
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape # h la chieucao w la chieu rong
                #lm.x va lm.y la toa do chuan hoa tu 0 toi 1
                # nhan w va h de ra toa do pixel thuc te
                cx, cy = int(lm.x*w), int(lm.y*h)
                listx_y.append([id, cx, cy])

            if len(listx_y) != 0:
                fingers = [] # mang luu trang thai ngon tay

                #======ktra ngon tay
                if listx_y[tipIds[0]][1] > listx_y[tipIds[0]-1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                for id in range(1, 5):
                    if listx_y[tipIds[id]][2] < listx_y[tipIds[id]-2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                totalfingers = fingers.count(1)

                cv2.putText(img, f'ngon tay:{totalfingers}',(10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)

                #===========Gui lenh cho vi dieu khien
                #neu goi 5 ngon va trang thai trc do chua mo 
                if totalfingers == 5 and current_command != 1:
                    cv2.putText(img,"trang thai: Mo cua",(10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)

                    # gui tin hieu 1 cho arduino 
                    if arduino:
                        arduino.write(b'1')
                        arduino.flush()

                    print("gui lenh: 1 de mo cua")
                    current_command = 1
                    time.sleep(0.3)  # tranh spam lenh

                elif totalfingers == 0 and current_command != 0:
                    cv2.putText(img,"trang thai dang dong cua",(10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

                    #gui tin hieu dong cua (0)
                    if arduino:
                        arduino.write(b'0')
                        arduino.flush()

                    print("gui lenh: 0 dong cua")
                    current_command = 0
                    time.sleep(0.3)

    cv2.imshow("My hand", img)  # 

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if arduino:
    arduino.close() # tat serial

cap.release() #tat cam
cv2.destroyAllWindows() # tat cac cua so cua open Cv
import cv2
import mediapipe as mp
import serial
import time
import firebase_admin
from firebase_admin import credentials, db
# định nghĩa cho firebase
try:
    cred = credentials.Certificate("serviceAccountKey.json")

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ai-doors-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

    # Node tổng
    root_ref = db.reference('Trangthaicua')
    # Node trạng thái hiện tại
    state_ref = db.reference('Trangthaicua/trang_thai_hien_tai')
    # Node log lịch sử
    log_ref = db.reference('Trangthaicua/logs')
    # Node lưu ngày cuối cùng hoạt động để kiểm tra reset
    last_date_ref = db.reference('Trangthaicua/last_active_date')

    print("--- Firebase connected ---")

except Exception as e:
    print(f"Firebase error: {e}")
    state_ref = None
    log_ref = None
#====== cấu hình arduino========#
arduino_port = 'COM4'
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
last_time = 0
cooldown = 1.5 

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

#========= ham reset log
def check_and_reset_logs():
    """Kiểm tra nếu sang ngày mới thì xóa log cũ"""
    current_date = time.strftime("%d/%m/%Y")
    
    # Lấy ngày cuối cùng được lưu trên Firebase
    db_date = last_date_ref.get()
    
    if db_date is not None and db_date != current_date:
        print(f"--- Sang ngày mới ({current_date}), đang xóa log cũ... ---")
        log_ref.delete() # Xóa sạch node logs
        # Cập nhật lại ngày mới vào Firebase
        last_date_ref.set(current_date)
    elif db_date is None:
        # Lần đầu chạy chưa có ngày, thì tạo ngày mới
        last_date_ref.set(current_date)
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
                now = time.time()
                can_send = now - last_time > cooldown

                #===========Gui lenh cho vi dieu khien
                #neu goi 5 ngon va trang thai trc do chua mo 
                #=========== Gửi lệnh cho vi điều khiển & Firebase ===========
                # TRƯỜNG HỢP MỞ CỬA
                if totalfingers == 5 and current_command != 1 and can_send:
                    
                    check_and_reset_logs() # Kiểm tra sang ngày mới để xóa log

                    cv2.putText(img, "OPEN DOOR", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    if arduino:
                        arduino.write(b'1')

                    if state_ref:
                        state_ref.set({
                            "status": "OPEN",
                            "value": 1,
                            "time": time.strftime("%H:%M:%S")
                        })

                    if log_ref:
                        log_ref.push({
                            "action": "OPEN",
                            "time": time.strftime("%H:%M:%S"),
                            "date": time.strftime("%d/%m/%Y")
                        })

                    current_command = 1
                    last_time = now # Cập nhật mốc thời gian để tính cooldown
                    time.sleep(0.3) # Delay vật lý
                    print(">> Đã mở cửa")

                # TRƯỜNG HỢP ĐÓNG CỬA
                elif totalfingers == 0 and current_command != 0 and can_send:
                    
                    check_and_reset_logs()

                    cv2.putText(img, "CLOSE DOOR", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    if arduino:
                        arduino.write(b'0')

                    if state_ref:
                        state_ref.set({
                            "status": "CLOSED",
                            "value": 0,
                            "time": time.strftime("%H:%M:%S")
                        })

                    if log_ref:
                        log_ref.push({
                            "action": "CLOSE",
                            "time": time.strftime("%H:%M:%S"),
                            "date": time.strftime("%d/%m/%Y")
                        })

                    current_command = 0
                    last_time = now
                    time.sleep(0.3)
                    print(">> Đã đóng cửa")
                   
    cv2.imshow("Smart Door AI", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

if arduino: arduino.close()
cap.release()
cv2.destroyAllWindows()

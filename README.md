# Smart Door AI - Hệ thống điều khiển cửa thông minh bằng cử chỉ tay

Dự án sử dụng Trí tuệ nhân tạo (Computer Vision) để nhận diện cử chỉ tay thông qua Camera, từ đó truyền tín hiệu điều khiển động cơ Servo đóng/mở cửa và đồng bộ dữ liệu lịch sử lên Cloud.

## 🚀 Tính năng chính
* Nhận diện cử chỉ tay "Mở/Đóng" thời gian thực bằng camera.
* Điều khiển động cơ Servo S90 xoay góc để gạt chốt cửa.
* Kết nối và cập nhật trạng thái, lưu log lịch sử hoạt động lên Firebase Realtime Database.

## 🛠 Linh kiện & Công nghệ sử dụng
* **Phần mềm/AI:** Python, OpenCV, MediaPipe (nhận diện bàn tay), Firebase Admin SDK.
* **Phần cứng:** Arduino (hoặc vi điều khiển tương đương), Động cơ Servo SG90.

## 📂 Cấu trúc mã nguồn
* `CodeCV2.py`: File Python xử lý hình ảnh từ camera, nhận diện cử chỉ và gửi dữ liệu lên Firebase / Serial.
* `Code_Servo_S90.ino`: Code Arduino nạp vào mạch để đọc dữ liệu và điều khiển Servo.

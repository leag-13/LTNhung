import cv2
import numpy as np
from lane_line_detection import *
from traffic_sign_detection import *

# Khởi tạo mô hình phân loại biển báo
traffic_sign_model = cv2.dnn.readNetFromONNX("traffic_sign_classifier.onnx")

def process_video():
    # Chọn nguồn video: 0 là camera, hoặc đường dẫn file video
    cap = cv2.VideoCapture(0)  # Hoặc cv2.VideoCapture('path/to/video.mp4')
    
    while True:
        # Đọc frame từ camera
        ret, frame = cap.read()
        
        if not ret:
            print("Không thể đọc frame")
            break
        
        # Tạo bản sao để vẽ
        draw = frame.copy()
        
        # Tính toán điều khiển
        throttle, steering_angle = calculate_control_signal(frame, draw=draw)
        
        # Phát hiện biển báo
        detect_traffic_signs(frame, traffic_sign_model, draw=draw)
        # Hiển thị thông tin điều khiển
        cv2.putText(draw, 
                    f"Throttle: {throttle:.2f}, Steering: {steering_angle:.2f}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, 
                    (0, 255, 0), 
                    2)
        
        # Hiển thị frame
        cv2.imshow("Lane and Traffic Sign Detection", draw)
        
        # Thoát nếu nhấn 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()

# Chạy chương trình
if __name__ == '__main__':
    process_video()

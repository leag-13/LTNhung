import cv2, time
import traffic_sign_detection as tsd        # file bạn đã cung cấp
from code_car import forward, backward, stop, turn_left, turn_right, set_speed
# -------------------------------  THÔNG SỐ  ---------------------------------
CAM_ID          = 0        # USB cam = 0; CSI cam Jetson khác id
DEFAULT_SPEED   = 40       # % PWM khi chạy thẳng / rẽ
SLOW_SPEED      = 25       # % PWM khi gặp biển walk
CMD_COOLDOWN    = 0.6      # giãn cách lệnh (giảm rung – giây)
CONF_THRESHOLD  = 0.50     # độ tin cậy tối thiểu
# ---------------------------  HÀM ĐIỀU KHIỂN  --------------------------------
def handle_cmd(cmd: str):
    """
    Nhận một trong 7 class → gọi hàm điều khiển tương ứng.
    Tuỳ thực tế bạn tinh chỉnh time.sleep() cho mượt.
    """
    if cmd == 'left':
        set_speed(DEFAULT_SPEED); turn_left();  time.sleep(0.5); forward()
    elif cmd == 'right':
        set_speed(DEFAULT_SPEED); turn_right(); time.sleep(0.5); forward()
    elif cmd == 'straight':
        set_speed(DEFAULT_SPEED); forward()
    elif cmd == 'stop':
        stop()
    elif cmd == 'walk':
        set_speed(SLOW_SPEED);   forward()    
    elif cmd == 'turn_around':
        set_speed(DEFAULT_SPEED); turn_left(); time.sleep(1.0); turn_left(); time.sleep(1.0); forward() #Thử cho xe Hai lần turn_left() liên tiếp ≈ quay đầu 180 °.
    # unknown → không can thiệp
    #Nếu test turn left hai lần không ổn có thể sử dụng hàm backward nhé anh em: (nữa update code sau)
    
# ------------------------------  VÒNG LẶP  -----------------------------------
def main():
    cap = cv2.VideoCapture(CAM_ID)
    if not cap.isOpened():
        print("❗ Không mở được camera"); return

    set_speed(DEFAULT_SPEED); forward()     
    last_cmd, last_time = 'straight', 0

    while True:
        ok, frame = cap.read()
        if not ok: break

        # --- Nhận dạng biển báo ---
        label, conf = tsd.detect_single_sign(frame, tsd.traffic_sign_model, CONF_THRESHOLD) 
        now = time.time()

        # --- Quyết định ---
        if conf >= CONF_THRESHOLD and label != 'unknown':
            if label != last_cmd or (now - last_time) > CMD_COOLDOWN:
                handle_cmd(label)
                last_cmd, last_time = label, now

        # --- DEBUG hiển thị ---
        cv2.putText(frame, f"{label}:{conf:.2f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        cv2.imshow("Sign-Based Drive", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- thoát ---
    cap.release()
    cv2.destroyAllWindows()
    stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop()

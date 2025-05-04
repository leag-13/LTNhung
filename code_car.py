import RPi.GPIO as GPIO
import time
import curses  # Thư viện để bắt phím từ bàn phím

# Thiết lập chế độ GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Khai báo các chân cho L298N
# Động cơ A
ENA = 22
IN2 = 17   # Enable cho động cơ A
IN1 = 27  # Input 1 cho động cơ A
 # Input 2 cho động cơ A

# Động cơ B
ENB = 25  # Enable cho động cơ B
IN3 = 24  # Input 3 cho động cơ B
IN4 = 23  # Input 4 cho động cơ B

# Thiết lập các chân GPIO
motor_pins = [ENA, IN1, IN2, ENB, IN3, IN4]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Khởi tạo PWM
pwm_a = GPIO.PWM(ENA, 1000)  # PWM tần số 1kHz
pwm_b = GPIO.PWM(ENB, 1000)  # PWM tần số 1kHz
pwm_a.start(100)  # Tốc độ 70%
pwm_b.start(100)  # Tốc độ 70%

# Định nghĩa các hàm điều khiển động cơ
def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def forward():
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)


def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def turn_left():
    # Động cơ A dừng/chậm lại, động cơ B tiến
    GPIO.output(IN1, GPIO.LOW)  # hoặc GPIO.LOW nếu muốn dừng hẳn bên trái
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    # Động cơ A tiến, động cơ B dừng/chậm lại
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)  # hoặc GPIO.LOW nếu muốn dừng hẳn bên phải
    GPIO.output(IN4, GPIO.LOW)
#Thêm hàm này:
def set_speed(speed):
    speed = int(speed)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    return f"Tốc độ: {speed}%"
# Hàm chính để điều khiển bằng bàn phím
def main(stdscr):
    # Không hiển thị phím nhấn
    curses.noecho()
    # Không cần nhấn Enter
    curses.cbreak()
    # Ẩn con trỏ
    curses.curs_set(0)
    # Cho phép stdscr nhận phím đặc biệt (Arrow keys, F1, ...)
    stdscr.keypad(True)

    # Xóa màn hình
    stdscr.clear()

    # Hiển thị hướng dẫn
    stdscr.addstr(0, 0, "Sử dụng phím mũi tên để điều khiển robot")
    stdscr.addstr(1, 0, "↑: Tiến, ↓: Lùi, ←: Trái, →: Phải")
    stdscr.addstr(2, 0, "Phím cách: Dừng, q: Thoát")
    stdscr.refresh()

    # Vòng lặp chính để bắt phím
    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            stdscr.addstr(4, 0, "Di chuyển: Tiến    ")
            forward()
        elif key == curses.KEY_DOWN:
            stdscr.addstr(4, 0, "Di chuyển: Lùi     ")
            backward()
        elif key == curses.KEY_LEFT:
            stdscr.addstr(4, 0, "Di chuyển: Trái    ")
            turn_left()
        elif key == curses.KEY_RIGHT:
            stdscr.addstr(4, 0, "Di chuyển: Phải    ")
            turn_right()
        elif key == ord(' '):  # Phím cách
            stdscr.addstr(4, 0, "Di chuyển: Dừng    ")
            stop()

        stdscr.refresh()

try:
    # Khởi chạy chương trình chính với curses
    curses.wrapper(main)

except Exception as e:
    print(f"Lỗi: {e}")

finally:
    # Đảm bảo dừng động cơ và giải phóng GPIO khi kết thúc
    stop()
    pwm_a.stop()
    pwm_b.stop()
    GPIO.cleanup()
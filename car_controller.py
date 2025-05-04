from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Hàm thiết lập GPIO - được gọi khi khởi động ứng dụng
def setup_gpio():
    # Đảm bảo GPIO đã được dọn dẹp
    try:
        GPIO.cleanup()
    except:
        pass

    # Thiết lập chế độ GPIO và tắt cảnh báo
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Khai báo các chân
    global ENA, IN1, IN2, ENB, IN3, IN4
    ENA = 22
    IN1 = 27
    IN2 = 17
    ENB = 25
    IN3 = 24
    IN4 = 23

    # Thiết lập các chân GPIO
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    # Khởi tạo PWM
    global pwm_a, pwm_b
    pwm_a = GPIO.PWM(ENA, 1000)
    pwm_b = GPIO.PWM(ENB, 1000)
    pwm_a.start(30)  # Tốc độ 30%
    pwm_b.start(30)  # Tốc độ 30%

    print("GPIO đã được thiết lập thành công")

# Hàm điều khiển động cơ
def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    return "Dừng"

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    return "Tiến"

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    return "Lùi"

def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    return "Trái"

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    return "Phải"

def set_speed(speed):
    speed = int(speed)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    return f"Tốc độ: {speed}%"

# Trang web chính
@app.route('/')
def index():
    return render_template('index.html')

# API điều khiển
@app.route('/control/<command>')
def control(command):
    if command == 'forward':
        return forward()
    elif command == 'backward':
        return backward()
    elif command == 'left':
        return left()
    elif command == 'right':
        return right()
    elif command == 'stop':
        return stop()
    else:
        return "Lệnh không hợp lệ!"

@app.route('/speed/<value>')
def speed(value):
    return set_speed(value)

if __name__ == '__main__':
    try:
        # Thiết lập GPIO trước khi chạy Flask
        setup_gpio()

        # Đảm bảo tất cả dừng khi khởi động
        stop()

        # Khởi động Flask KHÔNG sử dụng chế độ debug
        print("Khởi động máy chủ web...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Lỗi khi khởi động ứng dụng: {e}")
    finally:
        # Đảm bảo dừng lại và giải phóng GPIO khi kết thúc
        try:
            stop()
            pwm_a.stop()
            pwm_b.stop()
            GPIO.cleanup()
            print("Đã giải phóng tài nguyên GPIO")
        except Exception as e:
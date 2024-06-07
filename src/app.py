from flask import Flask, request, jsonify, send_from_directory
import serial
import RPi.GPIO as GPIO

app = Flask(__name__, static_folder='static')

SERIAL_PORT = "/dev/ttyS0"  # GPIO14 (TX) と GPIO15 (RX)
PIN_20 = 12  # GPIO 12

SUPPORTED_COMMANDS = {
    "up": bytearray(b'\x9b\x06\x02\x01\x00\xfc\xa0\x9d'),
    "down": bytearray(b'\x9b\x06\x02\x02\x00\x0c\xa0\x9d'),
    "m": bytearray(b'\x9b\x06\x02\x20\x00\xac\xb8\x9d'),
    "wake_up": bytearray(b'\x9b\x06\x02\x00\x00\x6c\xa1\x9d'),
    "preset_1": bytearray(b'\x9b\x06\x02\x04\x00\xac\xa3\x9d'),
    "preset_2": bytearray(b'\x9b\x06\x02\x08\x00\xac\xa6\x9d'),
    "preset_3": bytearray(b'\x9b\x06\x02\x10\x00\xac\xac\x9d'),
    "preset_4": bytearray(b'\x9b\x06\x02\x00\x01\xac\x60\x9d'),
}

class LoctekMotion:
    def __init__(self, serial, pin_20):
        self.serial = serial
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_20, GPIO.OUT)
        GPIO.output(pin_20, GPIO.HIGH)

    def execute_command(self, command_name: str):
        command = SUPPORTED_COMMANDS.get(command_name)
        if not command:
            raise Exception("Command not found")
        self.serial.write(command)

    def decode_seven_segment(self, byte):
        binaryByte = bin(byte).replace("0b", "").zfill(8)
        decimal = False
        if binaryByte[0] == "1":
            decimal = True
        digit_map = {
            "0111111": 0, "0000110": 1, "1011011": 2, "1001111": 3,
            "1100110": 4, "1101101": 5, "1111101": 6, "0000111": 7,
            "1111111": 8, "1101111": 9, "1000000": 10
        }
        digit = digit_map.get(binaryByte[1:], -1)
        return digit, decimal

    def current_height(self):
        history = [None] * 5
        msg_type, msg_len, valid = 0, 0, False
        while True:
            try:
                data = self.serial.read(1)
                if history[0] == 0x9b:
                    msg_len = data[0]
                if history[1] == 0x9b:
                    msg_type = data[0]
                if history[2] == 0x9b:
                    if msg_type == 0x12 and msg_len == 7 and data[0] != 0:
                        valid = True
                if history[4] == 0x9b and valid and msg_len == 7:
                    height1, decimal1 = self.decode_seven_segment(history[1])
                    height2, decimal2 = self.decode_seven_segment(history[0])
                    height3, decimal3 = self.decode_seven_segment(data[0])
                    if height1 < 0 or height2 < 0 or height3 < 0:
                        return "Display Empty"
                    finalHeight = height1 * 100 + height2 * 10 + height3
                    if decimal1 or decimal2 or decimal3:
                        finalHeight /= 10
                    return finalHeight
                history = [data[0]] + history[:-1]
            except Exception as e:
                return str(e)

def create_loctek_instance():
    ser = serial.Serial(SERIAL_PORT, 9600, timeout=500)
    return LoctekMotion(ser, PIN_20)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/command", methods=["POST"])
def command():
    try:
        command = request.form.get('command')
        locktek = create_loctek_instance()
        locktek.execute_command(command)
        return jsonify({"status": "success", "command": command}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/height", methods=["GET"])
def height():
    try:
        locktek = create_loctek_instance()
        height = locktek.current_height()
        return jsonify({"status": "success", "height": height}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

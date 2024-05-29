from flask import Flask, request, jsonify
import serial
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

SERIAL_PORT = "/dev/ttyS0" # GPIO14 (TX) and GPIO15 (RX)
PIN_20 = 12 # GPIO 12

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

class LoctekMotion():

    def __init__(self, serial, pin_20):
        """Initialize LoctekMotion"""
        self.serial = serial

        # Or GPIO.BOARD - GPIO Numbering vs Pin numbering
        GPIO.setmode(GPIO.BCM)

        # Turn desk in operating mode by setting controller pin20 to HIGH
        # This will allow us to send commands and to receive the current height
        GPIO.setup(pin_20, GPIO.OUT)
        GPIO.output(pin_20, GPIO.HIGH)

    def execute_command(self, command_name: str):
        """Execute command"""
        command = SUPPORTED_COMMANDS.get(command_name)

        if not command:
            raise Exception("Command not found")

        self.serial.write(command)

    def decode_seven_segment(self, byte):
        binaryByte = bin(byte).replace("0b","").zfill(8)
        decimal = False
        if binaryByte[0] == "1":
            decimal = True
        if binaryByte[1:] == "0111111":
            return 0, decimal
        if binaryByte[1:] == "0000110":
            return 1, decimal
        if binaryByte[1:] == "1011011":
            return 2, decimal
        if binaryByte[1:] == "1001111":
            return 3, decimal
        if binaryByte[1:] == "1100110":
            return 4, decimal
        if binaryByte[1:] == "1101101":
            return 5, decimal
        if binaryByte[1:] == "1111101":
            return 6, decimal
        if binaryByte[1:] == "0000111":
            return 7, decimal
        if binaryByte[1:] == "1111111":
            return 8, decimal
        if binaryByte[1:] == "1101111":
            return 9, decimal
        if binaryByte[1:] == "1000000":
            return 10, decimal
        return -1, decimal

    def current_height(self):
        history = [None] * 5
        msg_type = 0
        msg_len = 0
        valid = False
        while True:
            try:
                # read in each byte
                data = self.serial.read(1)
                # 9b starts the data
                # the value after 9b has the length of the packet
                if history[0] == 0x9b:
                    msg_len = data[0]
                if history[1] == 0x9b:
                    msg_type = data[0]
                if history[2] == 0x9b:
                    if msg_type == 0x12 and msg_len == 7:
                        if data[0] == 0:
                            print("height is empty                ", end='\r')
                        else:
                            valid = True
                if history[3] == 0x9b:
                    if valid == True:
                         pass
                if history[4] == 0x9b:
                    if valid == True and msg_len == 7:
                        height1, decimal1 = self.decode_seven_segment(history[1])
                        height1 = height1 * 100
                        height2, decimal2 = self.decode_seven_segment(history[0])
                        height2 = height2 * 10
                        height3, decimal3 = self.decode_seven_segment(data[0])
                        if height1 < 0 or height2 < 0 or height3 < 0:
                            print("Display Empty","          ",end='\r')
                        else:
                            finalHeight = height1 + height2 + height3
                            decimal = decimal1 or decimal2 or decimal3
                            if decimal == True:
                                finalHeight = finalHeight/10
                            print("Height:",finalHeight,"       ",end='\r')
                history[4] = history[3]
                history[3] = history[2]
                history[2] = history[1]
                history[1] = history[0]
                history[0] = data[0]
            except Exception as e:
                print(e)
                break

def create_loctek_instance():
    ser = serial.Serial(SERIAL_PORT, 9600, timeout=500)
    return LoctekMotion(ser, PIN_20)

@app.route("/command", methods=["POST"])
def command():
    try:
        req_data = request.get_json()
        command = req_data['command']
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
        return jsonify({"status": "success", "height":height}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

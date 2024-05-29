from flask import Flask, request, jsonify
import serial
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<html><body><h1>sample</h1></body></html>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import bluetooth
from gpiozero import LED
import time
import threading
import os
import RPi.GPIO as GPIO
import socket


def connect_to_arduino(): # BT 연결
    global arduino_socket
    global last_connected_device
    global target_name
   
    while True:
        while arduino_socket == 0:
            nearby_devices = bluetooth.discover_devices(duration=4, lookup_names=True, lookup_class=False)
            for addr, name in nearby_devices:
                if target_name in name:
                    if addr != last_connected_device:  # Check if it's a new device
                        last_connected_device = addr  # Store the new device's address
                        print(f"Found {target_name} at address {addr}")

                        try:
                            arduino_socket = bluetooth.BluetoothSocket(
                                bluetooth.RFCOMM)
                            arduino_socket.connect((addr, 1))
                            print("Connected to Arduino successfully!")
                            send_to_arduino("F")
                            if GPIO.input(RED_PIN) == GPIO.HIGH: # 연결 시 빨간 불 일 경우
                                os.system("mpg321 red1.mp3")
                            if GPIO.input(GREEN_PIN) == GPIO.HIGH: # 연결 시 초록 불 일 경우
                                os.system("mpg321 green1.mp3")

                        except Exception as e:
                            print("Error while connecting to Arduino:", e)
                            arduino_socket = 0
                    else:
                        time.sleep(5)

            if arduino_socket == 0:
                print(f"{target_name} not found nearby. Retrying in 5 seconds...")
                time.sleep(5)


def disconnect_from_arduino():
    global arduino_socket
    if arduino_socket != 0:
        arduino_socket.close()
        arduino_socket = 0
        print("Disconnected from Arduino.")


def send_to_arduino(message):
    global arduino_socket
    try:
        if arduino_socket != 0:
            arduino_socket.send(message.encode())
            print(f"Sent '{message}' to Arduino.")
    except Exception as e:
        print("Error while sending data to Arduino:", e)


def bt_block():
    global last_connected_device
    time.sleep(120)  # Wait for block duration
    last_connected_device = 0  # Unblock the device's address
    print("block end")


def play_sound_bird():
    while stop_flag.is_set():
        os.system("mpg321 output10.mp3")
        time.sleep(2)


def play_sound_green():
    send_to_arduino("G")
    os.system("killall mpg321")
    os.system("mpg321 output8.mp3")
    os.system("mpg321 output5.mp3")
    disconnect_from_arduino()
    stop_flag.set()


def play_sound_flicker():
    os.system("killall mpg321")
    os.system("mpg321 output6.mp3")


def pedestrian_traffic_light():
    global arduino_socket
    flag_BT = False
    while True:
        red_led.on()
        green_led.off()

        if flag_BT is True: # 연결된 BT 검색 중지
            os.system("killall mpg321")
            os.system("mpg321 outred.mp3")
            block = threading.Thread(target=bt_block)
            block.start()
            flag_BT = False

        time.sleep(30) # 빨간 불 30초
        green_led.on()
        red_led.off()

        if arduino_socket != 0: # 아두이노 연결 확인
            flag_BT = True
            sound_green = threading.Thread(target=play_sound_green)
            sound_green.start()

            sound_bird = threading.Thread(target=play_sound_bird)
            sound_bird.start()

        time.sleep(20) # 녹색 불 20초

        if flag_BT is True:
            sound_flicker = threading.Thread(target=play_sound_flicker)
            sound_flicker.start()

        i = 0
        while i <= 15:
            green_led.off()
            time.sleep(0.5)
            green_led.on()
            time.sleep(0.5)
            i += 1

        stop_flag.clear()


RED_PIN = 27
GREEN_PIN = 22

red_led = LED(RED_PIN)
green_led = LED(GREEN_PIN)

arduino_socket = 0  # Bluetooth socket connected to Arduino
last_connected_device = 0  # Store the last connected device's address
blocked_device = 0  # Store the blocked device's address
target_name = "VISI"  # 아두이노의 블루투스 이름

stop_flag = threading.Event()

connect_thread = threading.Thread(target=connect_to_arduino)
connect_thread.start()
pedestrian_traffic_light()

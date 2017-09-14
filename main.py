import paramiko
import ftplib
import urllib.request
import re
import Robot
import RPi.GPIO as GPIO
import time


def download_file_ssh(uri):
    ssh_client=paramiko.SSHClient()
    ssh_hn = "10.186.239.3"
    ssh_un = "pi"
    ssh_pw = "raspberry"
    remote_file = "/home/pi/sftp/actions.json"

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=ssh_hn, username=ssh_un, password=ssh_pw)

    ftp_client = ssh_client.open_sftp()
    ftp_client.get(remote_file, "./actions.json")
    ftp_client.close()
    return True


def download_file_ftp(uri):
    ip = "10.186.239.3"
    username = "pi"
    pw = "raspberry"
    filename = "actions.json"
    ftp = ftplib.FTP(ip)
    ftp.login(username, pw)
    ftp.retrbinary("RETR " + filename, open("./actions.json", 'wb').write)
    ftp.quit()
    return True


def download_file_http(uri):
    urllib.request.urlretrieve(uri, "./actions.json")
    return True


def determine_download_method(uri):
    if uri.startswith("ftp://"):
        download_file_ftp(uri)
    elif uri.startswith("http://"):
        download_file_http(uri)
    elif uri.startswith("ssh://"):
        download_file_ssh(uri)
    else:
        raise ValueError("Invalid method")
    return True


def get_instructions(uri):
    """ Creates and returns a list 'actions_list' where each time in the list contains:
    index0 - action to perform, index1 - time to perform for """

    with open("./actions.json") as f:
        file = f.read()
    actions_list = re.findall(r'"action": "(\w*)",\n\s*"time": (\d*)', file, re.MULTILINE)
    for x in actions_list:
        print("Action to perform: " + x[0] + " Time to perform for: " + x[1])
    return actions_list


def follow_instructions(actions_list):
    """Work In Progress
    """

    robot = Robot.Robot(left_trim=0, right_trim=0)
    pin_R = 12
    pin_G = 32
    pin_B = 36
    BuzzerPin = 16
    RIGHT = 15  # GPIO 22 pin 15 (Right side sensor)
    LEFT = 13  # GPIO 27 pin 13 (Left side sensor)

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_R, GPIO.OUT)
    GPIO.setup(pin_G, GPIO.OUT)
    GPIO.setup(pin_B, GPIO.OUT)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.setup(RIGHT, GPIO.IN)
    GPIO.setup(LEFT, GPIO.IN)

    try:
        GPIO.output(pin_G, 1)
        for _ in range(4):
            GPIO.output(BuzzerPin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(BuzzerPin, GPIO.LOW)
        GPIO.output(pin_G, 0)
        for action in actions_list:
            if action[0] == "forward":
                robot.forward(150, action[1])
            elif action[0] == "backward":
                robot.backward(150, action[1])
            elif action[0] == "left":
                robot.left(150, action[1])
            elif action[0] == "right":
                robot.right(150, action[1])
            elif action[0] == "play_sound":
                GPIO.output(BuzzerPin, GPIO.HIGH)
                time.sleep(action[1])
                GPIO.output(BuzzerPin, GPIO.LOW)
            elif action[0] == "led_blue":
                GPIO.output(pin_B, 1)
                time.sleep(action[1])
                GPIO.output(pin_B, 0)
            elif action[0] == "led_green":
                GPIO.output(pin_G, 1)
                time.sleep(action[1])
                GPIO.output(pin_G, 0)
            elif action[0] == "led_red":
                GPIO.output(pin_R, 1)
                time.sleep(action[1])
                GPIO.output(pin_R, 0)
            elif action[0] == "stop":
                GPIO.cleanup()
                return True
            else:
                GPIO.output(pin_R, 1)
                GPIO.output(BuzzerPin, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(BuzzerPin, GPIO.LOW)
                GPIO.output(pin_R, 0)
                GPIO.cleanup()
                return True
    except KeyboardInterrupt:
        GPIO.cleanup()


def main():
    uri = "http://10.186.239.3/actions.json"
    determine_download_method(uri)
    actions_list = get_instructions("./actions.json")
    if actions_list: follow_instructions(actions_list)

if __name__ == "__main__":
    main()

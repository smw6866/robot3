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
        print()
    return actions_list


def follow_instructions(list):
    """Work In Progress
    """

    robot = Robot.Robot(left_trim=0, right_trim=0)
    pin_R = 12
    pin_G = 32
    pin_B = 36
    ObstaclePin = 11
    BuzzerPin = 16
    RIGHT = 15  # GPIO 22 pin 15 (Right side sensor)
    LEFT = 13  # GPIO 27 pin 13 (Left side sensor)
    buzzerstate = 0

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_R, GPIO.OUT)
    GPIO.setup(pin_G, GPIO.OUT)
    GPIO.setup(pin_B, GPIO.OUT)
    GPIO.setup(ObstaclePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.setup(RIGHT, GPIO.IN)
    GPIO.setup(LEFT, GPIO.IN)

    try:
        while True:
            if 0 != GPIO.input(ObstaclePin):
                GPIO.output(pin_G, 1)
                if GPIO.input(RIGHT) == 1 and GPIO.input(LEFT) == 1:
                    robot.forward(100)
                    print("Both=1")
                elif GPIO.input(LEFT) == 1 and GPIO.input(RIGHT) == 0:
                    robot.left(100)
                    print("Left=1")
                elif GPIO.input(RIGHT) == 1 and GPIO.input(LEFT) == 0:
                    robot.right(100)
                    print("Right=1")
                elif GPIO.input(RIGHT) == 0 and GPIO.input(LEFT) == 0:
                    robot.forward(100)
                    print("No Signal")
            if 0 == GPIO.input(ObstaclePin):
                startTime = time.time()
            while 0 == GPIO.input(ObstaclePin):
                now = time.time()
                if (now - startTime) >= 5 and buzzerstate != 1:
                    buzzerstate = 1
                    print("Activating Buzzer")
                    GPIO.output(BuzzerPin, GPIO.HIGH)
                GPIO.output(pin_G, 0)
                GPIO.output(pin_R, 1)
                robot.forward(0)
                robot.left(0)
                robot.right(0)
            GPIO.output(BuzzerPin, GPIO.LOW)
            buzzerstate = 0
            GPIO.output(pin_G, 0)
            GPIO.output(pin_R, 0)
            GPIO.output(pin_B, 0)
    except KeyboardInterrupt:
        GPIO.cleanup()


def main():
    uri = "http://10.186.239.3/actions.json"
    determine_download_method(uri)
    get_instructions("./actions.json")

if __name__ == "__main__":
    main()

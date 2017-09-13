import paramiko
import ftplib
import urllib.request
import re

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

def follow_instructions(uri):
    with open("./actions.json") as f:
        file = f.read()
    d = re.findall(r'"action": "(\w*)",\n\s*"time": (\d*)', file, re.MULTILINE)
    for x in d:
        print("Action to perform: " + x[0] + " Time to perform for: " + x[1])
        print()
def main():
    uri = "http://10.186.239.3/actions.json"
    determine_download_method(uri)
    follow_instructions("./actions.json")

if __name__ == "__main__":
    main()

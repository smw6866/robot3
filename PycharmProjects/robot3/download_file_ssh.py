import paramiko

ssh_client=paramiko.SSHClient()
ssh_hn = "10.186.239.3"
ssh_un = "pi"
ssh_pw = "raspberry"
local_filepath = "./actions.json"
remote_file = "/home/pi/sftp/actions.json"

ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=ssh_hn,username=ssh_un,password=ssh_pw)

ftp_client = ssh_client.open_sftp()
ftp_client.get(remote_file,local_filepath)
ftp_client.close()

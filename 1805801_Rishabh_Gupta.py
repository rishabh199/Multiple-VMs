#first run this command in both server and client
#cd .ssh
#ssh-keygen
#ssh-copy-id username@ip address of other vm to which you want to send rsa key
import paramiko
import pandas as pd
from getpass import getpass
import time
import email,smtplib,ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
hosts = ["192.168.1.10"] #Team please write  your vm ip address to which you want to connect 
def sendCSV():
    subject = "Perfromance data of vitrual machines"
    body = "This is an email with attachment sent developer"
    sender_email = "phantomprince338@gmail.com" #write email id of sender
    receiver_email = "rishabhgupta99779@gmail.com"#write email id of receiver
    password = "rishi99779" #write your own email id password

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "/home/osboxes/result.csv"  # In same directory as script

    # Open CSV file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
def generateCSV(host):
    username = "osboxes"
    headerList=['USER','RAM USAGE %','MEMORY USAGE %','COLLECTED TIME STAMP']
    cmd=['top  -b -n1 > test.txt','cat test.txt | sed -r \'s/[[:space:]]+/,/g\' | grep osboxes > test.csv',
    'cat test.csv | cut -d \',\' -f 3,10,11,12 > result.csv',
    'cat result.csv','scp result.csv osboxes@192.168.1.7:']
    session = paramiko.SSHClient()
    session.load_system_host_keys()
    session.connect(hostname=host,
                    username=username)
    for cmds in cmd:
        stdin,stdout,stderr = session.exec_command(cmds)
        time.sleep(5)
        print(stdout.read().decode())
        print(stderr.read().decode())
    session.close()
    file =pd.read_csv("/home/osboxes/result.csv") #Give the path of your csv file
    print("\n Modified file")
    file.to_csv("/home/osboxes/result.csv",header=headerList,index=False)
    file2=pd.read_csv("/home/osboxes/result.csv")
    print(file2)
    
def job(hosts):
    for host in hosts:
        generateCSV(host)
        sendCSV()
    

schedule.every(20).seconds.do(job,hosts)
while True:
    schedule.run_pending()
    time.sleep(1)
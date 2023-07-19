import os
import socket
import sys
import read_config
import re
import datetime
import hmac
import base64
import random
import string
import secrets
import read_email
PERSONAL_ID = '10C1B1'
PERSONAL_SECRET = '0f340ef23c81dec70a6b07f6f4504b44'

def get_email_files(send_path: str):
    files = [f for f in os.listdir(send_path) if os.path.isfile(os.path.join(send_path, f))]
    emails = []
    for file in files:
        if "txt" in file:
            emails.append(file)
    return emails

def valid_email(send_path: str,filename: str):
    if not read_email.all_fields_exist(send_path,filename):
        return False
    if not read_email.right_order(send_path,filename):
        return False
    if not read_email.check_non_empty(send_path,filename):
        return False
    if not read_email.check_from(send_path,filename):
        return False
    if not read_email.check_to(send_path,filename):
        return False
    if not read_email.check_date(send_path,filename):
        return False
    return True

def client_auth(id,secret,challenge):
	decode_challenge = base64.b64decode(challenge).decode()
	digest = hmac.new(secret.encode(),decode_challenge.encode(),"md5")
	hex_digest = digest.hexdigest()
	rep = id + " " + hex_digest
	rep_base64 = rep.encode('ascii')
	rep_base64byte = base64.b64encode(rep_base64).decode()
	return rep_base64byte

def send_email(client_sock: socket.socket, send_path: str,filename: str, challenge: str):
    if challenge != "":
        print("S: " + challenge,end="",flush=True)
        challenge = challenge.replace("334 ","")
        auth_reply = client_auth(PERSONAL_ID,PERSONAL_SECRET,challenge) + "\r\n"
        client_sock.send(auth_reply.encode())
        print("C: " + auth_reply,end="",flush=True)
        auth_result = client_sock.recv(1024).decode()
        print("C: " + auth_result,end="",flush=True)
    from_content = read_email.get_from(send_path,filename)
    to_content = read_email.get_to(send_path,filename)
    date_content = read_email.get_date(send_path,filename)
    subject_content = read_email.get_subject(send_path,filename)
    body_content = read_email.get_body(send_path,filename)

    
    from_content = "MAIL FROM:"+ from_content + "\r\n"
    client_sock.send(from_content.encode())
    from_rep = client_sock.recv(1024).decode()
    print("C: {}".format(from_content),end="",flush=True)
    print("S: " + from_rep,end="",flush=True)

    for content in to_content:
        content = "RCPT TO:" + content  + "\r\n"
        client_sock.send(content.encode())
        rcpt_rep = client_sock.recv(1024).decode()
        print("C: {}".format(content),end="",flush=True)
        print("S: " + rcpt_rep,end="",flush=True)
 
    client_sock.send("DATA\r\n".encode())
    data_rep = client_sock.recv(1024).decode()
    print("C: DATA\r\n",end="",flush=True)
    print("S: " + data_rep,end="",flush=True)

    date_content = "Date: " + date_content + "\r\n"
    client_sock.send((date_content).encode())
    date_rep = client_sock.recv(1024).decode()
    print("C: " + date_content,end="",flush=True)
    print("S: " + date_rep,end="",flush=True)

    subject_content = "Subject: " + subject_content + "\r\n"
    client_sock.send(subject_content.encode())
    subject_rep = client_sock.recv(1024).decode()
    print("C: {}".format(subject_content),end="",flush=True)
    print("S: " + subject_rep,end="",flush=True)

    for content in body_content:
        client_sock.send((content + "\r\n").encode())
        body_rep = client_sock.recv(1024).decode()
        print("C: {}".format(content+ "\r\n"),end="",flush=True)
        print("S: " + body_rep,end="",flush=True)
    
    client_sock.send(".\r\n".encode())
    end_body_rep = client_sock.recv(1024).decode()
    print("C: .\r\n",end="",flush=True)
    print("S: " + end_body_rep,end="",flush=True)

    client_sock.send("QUIT\r\n".encode())
    quit_rep = client_sock.recv(1024).decode()
    print("C: QUIT\r\n",end="",flush=True)
    print("S: " + quit_rep,end="",flush=True)

def main():
    try:
        config = sys.argv[1]
    except IndexError:
        sys.exit(1)

    read_config.config_exists(config)
    read_config.client_config_check(config)
    send_path, server_port = read_config.read_client_config(config)
    emails = sorted(get_email_files(send_path))
    valid_emails = []
    for email in emails:
        if valid_email(send_path,email):
            valid_emails.append(email)
    if len(valid_emails) == 0:
        sys.exit(0)
    i = 0
    while i < len(valid_emails):
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_sock.connect(("localhost",server_port))
        except ConnectionRefusedError as e:
            print("C: Cannot establish connection")
            sys.exit(3)
        
        try:
            service_ready = client_sock.recv(1024).decode()
            print("S: " + service_ready,end="",flush=True)
            client_sock.send(b"EHLO 127.0.0.1\r\n")
            print("C: EHLO 127.0.0.1\r\n",end="",flush=True)
            ehlo_rep = client_sock.recv(1024).decode()
            print("S: 250 127.0.0.1\r\n",end="",flush=True)
            challenge = ""
            if "auth" in valid_emails[i]:
                print("S: 250 AUTH CRAM-MD5\r\n",end="",flush=True)
                client_sock.send(b"AUTH CRAM-MD5\r\n")
                print("C: AUTH CRAM-MD5\r\n",end="",flush=True)
                challenge = client_sock.recv(1024).decode()
            send_email(client_sock,send_path,valid_emails[i],challenge)
        except(ConnectionAbortedError):
            print("C: Connection lost")
            sys.exit(3)
        i += 1
    client_sock.close()

if __name__ == '__main__':
    main()
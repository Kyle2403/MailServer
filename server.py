import os
import socket
import sys
import re
import datetime
import hmac
import base64
import random
import string
import secrets
PERSONAL_ID = '10C1B1'
PERSONAL_SECRET = '0f340ef23c81dec70a6b07f6f4504b44'

def config_exists(filename: str) -> None:
    try:
        f = open(filename,"r")
    except FileNotFoundError:
        exit(2)
    
def server_config_check(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    # surely lack property
    if len(lines) < 2:
        exit(2)
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    #lack "=" on some lines
    if len(ls) != 2*len(lines):
        exit(2)
    # lack a property
    if "inbox_path" not in ls or "server_port" not in ls:
        exit(2)
    # property mentioned more than once
    for part in ls:
        if ls.count(part) != 1 and part == "inbox_path":
            exit(2)
        if ls.count(part) != 1 and part == "server_port":
            exit(2)
    # port is not an int
    i = ls.index("server_port")
    try:
        port = int(ls[i+1])
    except:
        exit(2)
    # port smaller or equal to 1024
    if port <= 1024:
        exit(2)

def to_abs_path(send_path: str, filename: str) -> str:
    if "\n" in send_path:
        send_path=send_path.replace("\n","")
    if filename != "":
        if "~" in send_path:
            return os.path.expanduser(send_path)+"/"+filename
        if os.path.isabs(send_path):
            filename = send_path + "/" + filename
        if not os.path.isabs(send_path):
            if "." not in send_path:
                filename = os.getcwd() + send_path + "/" + filename
            else:
                send_path = send_path.replace(".","",1)
                filename = os.getcwd() + send_path + "/" + filename
    else:
        if "~" in send_path:
            return os.path.expanduser(send_path)
        if os.path.isabs(send_path):
            return send_path
        if not os.path.isabs(send_path):
            if "." not in send_path:
                filename = os.getcwd() + send_path
            else:
                send_path = send_path.replace(".","",1)
                filename = os.getcwd() + send_path
    return filename
    
def read_server_config(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    server_port = int(ls[ls.index("server_port") + 1])
    inbox_path = ls[ls.index("inbox_path") + 1]
    inbox_path = to_abs_path(inbox_path,"")
    return inbox_path,server_port

def email_match(where: str, data: str):
	if len(data.split(":")) != 2:
		return False
	email = data.split(":")[1]
	mail = "^<(\w(\w|\-)*(\.\w(\w|\-)*)*@{1}((\w((\w|\-)*\w)?)(\.\w((\w|\-)*\w)*){1})|\d*(\.\d*)*)>$"
	if email == "<>":
		return False
	if where == "From":
		if data.split(":")[0] != "MAIL FROM":
			return False
	else:
		if data.split(":")[0] != "RCPT TO":
			return False
	if re.fullmatch(mail,email):
		return True
	else:
		return False


def is_cmd(cmd):
    all_commands = ["EHLO","RSET","MAIL","RCPT","DATA","NOOP","QUIT","AUTH"]
    if cmd in all_commands:
        return True
    return False

def unix_timestamp(date_content):
    try:
        formated_date = datetime.datetime.strptime(date_content,'%a, %d %b %Y %H:%M:%S %z')
        unix_timestamp = datetime.datetime.timestamp(formated_date)
        return str(round(unix_timestamp)) + ".txt"
    except Exception as e:
        return "unknown.txt"

def extract_date(data_buffer):
    if "Date" not in data_buffer:
        return ""
    data = data_buffer.split("\r\n")
    pattern = "Date: "
    for line in data:
        if re.match(pattern,line):
            date_content = line.replace(pattern,"")
    try:
        date_content = date_content.replace("DATE: ","")
        datetime.datetime.strptime(date_content,'%a, %d %b %Y %H:%M:%S %z')
    except:
        return ""
    return date_content

def extract_subject(data_buffer):
    if "Subject" not in data_buffer:
        return ""
    data = data_buffer.split("\r\n")
    pattern = "Subject: "
    for line in data:
        if re.match(pattern,line):
            subject_content = line.replace(pattern,"")
    return subject_content

def extract_body(data_buffer) -> list:
    subject_content = "Subject: "+ extract_subject(data_buffer) + "\r\n"
    date_content = "Date: "+ extract_date(data_buffer) + "\r\n"
    body_content = data_buffer.replace(subject_content,"").replace(date_content,"").replace("DATA\r\n","").split("\r\n")
    body_content.remove("")
    return body_content

def save_email(inbox_path,source_buffer,des_buffer,data_buffer,auth):
    '''Save email and clear all buffers'''
    des_buffer = des_buffer.split(",")
    subject_content = extract_subject(data_buffer)
    date_content = extract_date(data_buffer)
    body_content = extract_body(data_buffer)
    if auth:
        filename = inbox_path + "/" + "auth." + unix_timestamp(date_content) 
    else:
        filename = inbox_path + "/" + unix_timestamp(date_content) 
    f = open(filename,"w")
    f.write("From: " + "<"+ source_buffer +">" + "\n")
    f.write("To: ")
    i = 0
    while i < len(des_buffer) - 1:
        f.write("<" + des_buffer[i] + ">" + ",")
        i += 1
    f.write("<" + des_buffer[i] + ">" + "\n")
    f.write("Date: " + extract_date(data_buffer) + "\n")
    f.write("Subject: " + extract_subject(data_buffer) + "\n")
    i = 0
    while i < len(body_content) - 1:
        f.write(body_content[i] + "\n")
        i += 1
    if len(body_content) > 0:
        f.write(body_content[i])
    return "","",""

def validate_ip(ip):
    ip = ip.split('.')
    if len(ip) != 4:
        return False
    for num in ip:
        if not num.isdigit():
            return False
        i = int(num)
        if i < 0 or i > 255:
            return False
    return True

def server_auth(id,secret,client_rep,challenge):
	client_rep = client_rep.encode('ascii')
	decode_rep = base64.b64decode(client_rep).decode()
	recalculate_digest = hmac.new(secret.encode(),base64.b64decode(challenge),"md5")
	recalculate_digest = recalculate_digest.hexdigest()
	client_digest = decode_rep.split(" ")[1]
	return client_digest == recalculate_digest

def response(data,source_buffer: str, des_buffer: str, commands: list,auth: bool,challenge_encode: str):
    rep = ""
    cmd = data.replace("\r\n","").replace("\t","").split(" ")[0]
    if len(list(cmd)) >= 4:
        cmd_ls = []
        i = 0
        while i < 4:
            cmd_ls.append(list(cmd)[i])
            i += 1
        cmd = "".join(cmd_ls)
    if is_cmd(cmd):
        data = data.replace("\r\n","").split(" ")
        if cmd == "EHLO":
            if len(data) != 2:
                rep = "501 Syntax error in parameters or arguments\r\n"
            else:
                ip = data[1]
                if validate_ip(ip):
                    rep = "250 127.0.0.1\r\n"+"250 AUTH CRAM-MD5\r\n"
                    source_buffer = ""
                    des_buffer = ""
                else:
                    rep = "501 Syntax error in parameters or arguments\r\n"
        if cmd == "RSET" or cmd == "NOOP" or cmd == "QUIT":
            if len(data) != 1 and cmd == "RSET":
                if "DATA" in commands:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
                else:
                    rep = "501 Syntax error in parameters or arguments\r\n"
            if len(data) == 1 and cmd == "RSET":
                if "DATA" in commands:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
                else:
                    source_buffer = ""
                    des_buffer = ""
                    rep = "250 Requested mail action okay completed\r\n"
            if len(data) != 1 and cmd == "NOOP":
                if "DATA" in commands:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
                else:
                    rep = "501 Syntax error in parameters or arguments\r\n"
            if len(data) == 1 and cmd == "NOOP":
                if "DATA" in commands:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
                else:
                    rep = "250 Requested mail action okay completed\r\n"
            if len(data) != 1 and cmd == "QUIT":
                if "DATA" in commands:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
                else:
                    rep = "501 Syntax error in parameters or arguments\r\n"
            if len(data) == 1 and cmd == "QUIT":
                if data[0] == "QUIT":
                    rep = "221 Service closing transmission channel\r\n"
                    commands = []
                    source_buffer = ""
                    des_buffer = ""
                else:
                    rep = "501 Syntax error in parameters or arguments\r\n"
        if cmd == "MAIL":
            if source_buffer != "" or "EHLO" not in commands:
                rep = "503 Bad sequence of commands\r\n"
            else:
                data = " ".join(data)
                if not email_match("From",data):
                    rep = "501 Syntax error in parameters or arguments\r\n"
                else:
                    rep = "250 Requested mail action okay completed\r\n"
                    des_buffer = ""
                    source_buffer = data.split("<")[1].strip(">")
        if cmd == "RCPT":
            if source_buffer == "":
                rep = "503 Bad sequence of commands\r\n"
            else:
                data = " ".join(data)
                if not email_match("To",data):
                    rep = "501 Syntax error in parameters or arguments\r\n"
                else:
                    rep = "250 Requested mail action okay completed\r\n"
                    if des_buffer != "":
                        des_buffer += "," + data.split("<")[1].strip(">")
                    else:
                        des_buffer += data.split("<")[1].strip(">")
        if cmd == "DATA":
            if source_buffer == "" or des_buffer == "":
                rep = "503 Bad sequence of commands\r\n"
            else:
                if len(data) != 1:
                    rep = "501 Syntax error in parameters or arguments\r\n"
                if len(data) == 1:
                    rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
        if cmd == "AUTH":
            if auth:
                rep = "503 Bad sequence of commands\r\n"
            else:
                if "DATA" in commands or "MAIL" in commands or "RCPT" in commands:
                    rep = "503 Bad sequence of commands\r\n"
                else:
                    if len(data) != 2:
                        rep = "501 Syntax error in parameters or arguments\r\n"
                    if len(data) == 2:
                        if data[1] != "CRAM-MD5":
                            rep = "504 Unrecognized authentication type\r\n"
                        else:
                            size = random.randint(16,128)
                            challenge_encode = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(size)).encode("ascii")
                            challenge_encode = base64.b64encode(challenge_encode).decode()
                            rep = "334 " + challenge_encode + "\r\n"
    else:
        if "EHLO" not in commands or "MAIL" not in commands or "RCPT" not in commands or "DATA" not in commands:
            if "AUTH" not in commands:
                rep = "500 Syntax error, command unrecognized\r\n"
            else:
                try:
                    credentials_ok = server_auth(PERSONAL_ID,PERSONAL_SECRET,data,challenge_encode)
                    if credentials_ok:
                        rep = "235 Authentication successful\r\n"
                        auth = True
                    else:
                        rep = "535 Authentication credentials invalid\r\n"
                except:
                    rep = "501 Syntax error in parameters or arguments\r\n"

        #if source_buffer == "" or des_buffer == "":
            #rep = "500 Syntax error, command unrecognized\r\n"
        if source_buffer != "" and des_buffer != "" and cmd != ".":
            rep = "354 Start mail input end <CRLF>.<CRLF>\r\n"
        
    return rep, source_buffer,des_buffer,commands,auth,challenge_encode


def main():
    commands = []
    source_buffer = ""
    des_buffer = ""
    data_buffer = ""
    
    challenge_encode = ""
    try:
        filename = sys.argv[1]
    except IndexError:
        exit(1)
    config_exists(filename)
    server_config_check(filename)
    inbox_path, server_port = read_server_config(filename)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_sock.bind(('localhost',server_port))
    except Exception as e:
        sys.exit(2)
    server_sock.listen(5)
    while True:
        auth = False
        conn,addr = server_sock.accept()
        print("S: 220 Service ready\r\n",end="",flush=True)
        conn.send(b"220 Service ready\r\n")
        stack = []
        while True:
            if stack == []:
                data = conn.recv(1024).decode()
            else:
                data = stack[0]
                stack.pop(0)
            if data.count("\r\n") > 1:
                data_lines = data.split("\r\n")
                data_lines.remove("")
                data = data_lines[0] + "\r\n"
                j = 1
                while j < len(data_lines):
                    stack.append(data_lines[j]+ "\r\n")
                    j += 1
            cmd = data.replace("\r\n","").replace("\t","").split(" ")[0]
            if is_cmd(cmd):
                commands.append(cmd)
            if not data:
                print("S: Connection lost\r\n",end="",flush=True)
                break
            if data.replace("\r\n","").upper() == "QUIT":
                rep,source_buffer,des_buffer,commands,auth,challenge_encode = response(data,source_buffer,des_buffer,commands,auth,challenge_encode)
                print("C: {}".format(data),end="",flush=True)
                print("S: "+ rep,end="",flush=True)
                conn.send(rep.encode())
                conn.close()
                break
            if data.replace("\r\n","").upper() == "SIGINT":
                break
            
            rep,source_buffer,des_buffer,commands,auth,challenge_encode = response(data,source_buffer,des_buffer,commands,auth,challenge_encode)
            if cmd == "QUIT":
                print("C: {}".format(data),end="",flush=True)
                print("S: "+ rep,end="",flush=True)
                conn.send(rep.encode())
            if cmd != "QUIT":
                print("C: {}".format(data),end="",flush=True)
                if rep == "250 127.0.0.1\r\n"+"250 AUTH CRAM-MD5\r\n":
                    print("S: 250 127.0.0.1\r\n",end="",flush=True)
                    print("S: 250 AUTH CRAM-MD5\r\n",end="",flush=True)
                    conn.send(b"250 127.0.0.1\r\n250 AUTH CRAM-MD5\r\n")
                else:
                    print("S: "+ rep,end="",flush=True)
                    conn.send(rep.encode())
            if (rep =="354 Start mail input end <CRLF>.<CRLF>\r\n" or rep == "") and cmd !=".":
                data_buffer += data
            if cmd == "." and rep == "":
                print("250 Requested mail action okay completed\r\n",end="",flush=True)
                conn.send(b"250 Requested mail action okay completed\r\n")
                source_buffer,des_buffer,data_buffer= save_email(inbox_path,source_buffer,des_buffer,data_buffer,auth)
        if data.replace("\r\n","").upper() == "SIGINT":
            print("S: SIGINT received, closing\r\n",end="",flush=True)
            conn.send(b"421 Service not available, closing transmission channel\r\n")
            conn.close()
            sys.exit(0)
if __name__ == '__main__':
    main()
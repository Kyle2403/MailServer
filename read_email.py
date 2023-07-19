import datetime
import os

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

def read_email(send_path: str, filename: str) -> list:
    filename = to_abs_path(send_path,filename)
    file = open(filename,"r")
    lines = file.readlines()
    return lines

def all_fields_exist(send_path: str, filename: str) -> bool:
    content = read_email(send_path, filename)
    from_exist = False
    to_exist = False
    date_exist = False
    subject_exist = False
    for line in content:
        if "From" in line:
            from_exist = True
        if "To" in line:
            to_exist = True
        if "Date" in line:
            date_exist = True
        if "Subject" in line:
            subject_exist = True
    if not from_exist or not to_exist or not date_exist or not subject_exist:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    return True

# chedk if fields are in order and if they only have 1 line as they should
def right_order(send_path: str, filename: str) -> bool:
    content = read_email(send_path,filename)
    if "From: " not in content[0]:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    if "To: " not in content[1]:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    if "Date: " not in content[2]:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    if "Subject: " not in content[3]:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    return True

def check_non_empty(send_path: str, filename: str):
    content = read_email(send_path,filename)
    from_content = content[0].replace("\n","").split(" ")
    if len(from_content) != 2 or from_content[1] == "":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    to_content = content[1].replace("\n","").split(" ")
    if len(to_content) != 2 or to_content[1] == "":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    date_content = content[2].replace("\n","").split(": ")
    if len(date_content) != 2 or date_content[1] == "":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    subject_content = content[3].replace("\n","").split(": ")
    if len(subject_content) != 2 or subject_content[1] == "":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    return True

def check_from(send_path: str, filename: str):
    content = read_email(send_path,filename)
    from_content = content[0].replace("\n","").split(" ")[1]
    if from_content == "<>":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    from_content = list(from_content)
    if from_content[0] != "<" or from_content[len(from_content) - 1] != ">":
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    return True

def check_to(send_path: str, filename: str):
    content = read_email(send_path,filename)
    to_content = content[1].replace("\n","").split(" ")[1]
    to_content = to_content.split(",")
    for mail in to_content:
        if mail == "<>":
            print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
            return False
        if "<" not in mail or ">" not in mail:
            print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
            return False
        mail = list(mail)
        if mail.index("<") != 0 or mail.index(">") != len(mail) - 1:
            print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
            return False
    return True

def check_date(send_path: str, filename: str):
    content = read_email(send_path,filename)
    date_content = content[2].replace("\n","").split(": ")[1]
    try:
        time = datetime.datetime.strptime(date_content,'%a, %d %b %Y %H:%M:%S %z')
    except:
        print("C: {}: Bad formation".format(to_abs_path(send_path,filename)))
        return False
    return True

def get_from(send_path: str, filename: str) -> str:
    content = read_email(send_path, filename)
    from_content = content[0].replace("\n","").split(" ")[1]
    return from_content

def get_to(send_path: str, filename: str) -> list:
    content = read_email(send_path,filename)
    to_content = content[1].replace("\n","").split(" ")[1]
    to_content = to_content.split(",")
    return to_content

def get_date(send_path: str, filename: str) -> str:
    content = read_email(send_path,filename)
    date_content = content[2].replace("\n","").split(": ")[1]
    return date_content

def get_subject(send_path: str, filename: str) -> str:
    content = read_email(send_path,filename)
    subject_content = content[3].replace("\n","").split(": ")[1]
    return subject_content

def get_body(send_path: str, filename: str):
    content = read_email(send_path,filename)
    body_content = []
    i = 4
    while i < len(content):
        body_content.append(content[i].replace("\n",""))
        i += 1
    return body_content

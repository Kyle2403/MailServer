import read_email
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

def client_config_check(filename: str):
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
    if "send_path" not in ls or "server_port" not in ls:
        exit(2)
    # property mentioned more than once
    for part in ls:
        if ls.count(part) != 1 and part == "send_path":
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

def read_client_config(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    server_port = int(ls[ls.index("server_port") + 1])
    send_path = ls[ls.index("send_path") + 1]
    send_path = read_email.to_abs_path(send_path,"")
    return send_path,server_port

def read_server_config(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    server_port = int(ls[ls.index("server_port") + 1])
    inbox_path = ls[ls.index("inbox_path") + 1]
    inbox_path = read_email.to_abs_path(inbox_path,"")
    return inbox_path,server_port

def spy_config_check(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    # surely lack property
    if len(lines) < 3:
        exit(2)
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    #lack "=" on some lines
    if len(ls) != 2*len(lines):
        exit(2)
    # lack a property
    if "client_port" not in ls or "spy_path" not in ls or "server_port" not in ls:
        exit(2)
    # property mentioned more than once
    for part in ls:
        if ls.count(part) != 1 and part == "spy_path":
            exit(2)
        if ls.count(part) != 1 and part == "server_port":
            exit(2)
        if ls.count(part) != 1 and part == "client_port":
            exit(2)
    # port is not an int
    i = ls.index("server_port")
    j = ls.index("client_port")
    try:
        server_port = int(ls[i + 1])
        client_port = int(ls[j + 1])
    except:
        exit(2)
    # port smaller or equal to 1024
    if server_port <= 1024 or client_port <= 1024:
        exit(2)
    if server_port == client_port:
        exit(2)

def read_spy_config(filename: str):
    f = open(filename,"r")
    lines = f.readlines()
    ls = []
    for line in lines:
        parts = line.split("=")
        ls.extend(parts)
    client_port = int(ls[ls.index("client_port") + 1])
    server_port = int(ls[ls.index("server_port") + 1])
    spy_path = ls[ls.index("spy_path") + 1]
    spy_path = read_email.to_abs_path(spy_path,"")
    return client_port,server_port,spy_path
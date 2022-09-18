import socket
import sys
import regex
import threading
from _thread import *
class Server():
    def __init__(self, host, port, root="./"):
        self.clients=[]
        self.root = root
        self.data = {}
        self.host = host
        self.port = port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((host, port))
        except OSError as e:
            print("Waiting for port to become available")
            error = True
            while error:
                try:
                    server.bind((host, port))
                    error = False
                except:
                    pass
        self.paths = {}
    def new_var(self, name, value):
        self.data.update({
            name: value
        })
    def add_path(self, path):
        self.paths.update({
            path:{
                "route": path,
                "type": "basic"
            }
        })
    def get_website(self, path):
        with open(self.root+path, "r") as f:
            final = f.read()
            reg = regex.findall("{\w*}", final)
            for x in reg:
                replace_str = x.replace("{", "").replace("}", "")
                final = final.replace(x,self.data[replace_str])
            return final
    def add_path_redirect(self, path, redirect):
        self.paths.update({
            path:{
                "route": redirect,
                "type": "basic"
            }
        })
    def add_path_function(self, path, function):
        self.paths.update({
            path:{
                "route": function,
                "type": "function"
            }
        })
    def add_path_function_wildcard(self, path, function):
        self.paths.update({
            path:{
                "route": function,
                "type": "function_wildcard"
            }
        })
    def get_path_data(self, path):
        if path in self.paths:
            if self.paths[path]["type"] == "basic":
                with open(self.root+self.paths[path]["route"], "r") as f:
                    final = f.read()
                    reg = regex.findall("{\w*}", final)
                    for x in reg:
                        replace_str = x.replace("{", "").replace("}", "")
                        final = final.replace(x,self.data[replace_str])
                return final
            else:
                return self.paths[path]["route"](path)
        else:
            return None
    def finish(self, client, addr, on_request=None, text=None):
        wc = False
        success = False
        if addr not in self.clients:
            self.clients.append(addr)
        try:
            # get path on website the client is trying to access
            path = client.recv(1024).decode()
            try:
                path_split = path.split(" ")[1]
            except:
                path_split = "/"
            if path_split in self.paths:
                if self.paths[path_split]["type"] == "basic":
                    success = True
                    with open(self.root+self.paths[path_split]["route"], "r") as f:
                        final = f.read()
                        reg = regex.findall("{\w*}", final)
                        for x in reg:
                            replace_str = x.replace("{", "").replace("}", "")
                            final = final.replace(x,self.data[replace_str])
                    request = "HTTP/1.1 200 OK\r\n\r\n"+final
                elif self.paths[path_split]["type"] == "function":
                    request = self.paths[path_split]["route"](path,addr)
                    if request == None:
                        self.clients.remove(addr)
                        client.close()
                        return
                    success = True
            #Check if path starts with any of the paths in function_wildcard
            for x in self.paths:
                if self.paths[x]["type"] == "function_wildcard":
                    if path_split.startswith(x):
                        wc = True
                        wc_used = True
                        print("Wildcard: "+x)
                        request = self.paths[x]["route"](path,addr)
                        success = True
                        if request == None:
                            self.clients.remove(addr)
                            client.close()
                            return
            else:
                if success == False:
                    final = "The specified link could not be found"
                    request = "HTTP/1.1 200 OK\r\n\r\n"+final
            client.send(request.encode())
            client.close()
            self.clients.remove(addr)
            if on_request != None:
                threading.Thread(target=on_request(path, request, addr)).start()
        except KeyboardInterrupt:
            print("[*] Exiting...")
            client.close()
            self.server.close()
            exit(0)
    def listen(self, on_request=None, text=None):
        threads = []
        ThreadCount = 0
        self.server.listen(4)
        while True:
            #Make a new thread for each client
            client, addr = self.server.accept()
            start_new_thread(self.finish, (client, addr, on_request, text))
            ThreadCount += 1
            print(ThreadCount)
def arg_parser():
    host = "localhost"
    port = 8080
    dev = False
    for x in sys.argv:
        if x == "--host":
            host = sys.argv[sys.argv.index(x)+1]
        if x == "--port":
            port = int(sys.argv[sys.argv.index(x)+1])
        if x == "--dev":
            dev = True
    return host, port, dev
def get_content_from_post(path):
    #Change an http post request to the text of the content recieved
    #returns None if no content is recieved
    content = None
    try:
        content = path.split("\r\n\r\n")[1]
    except:
        pass
    return content
def extract_path(path):
    #Code taken from pogcoin-cli
    path = path.replace("HTTP/1.1", "").split("\n")[0].replace(" \r", "").replace("GET ", "")[1:].split("/")[1:]
    return path
basic_http_html = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
basic_http_js = "HTTP/1.1 200 OK\r\nContent-Type: application/javascript\r\n\r\n"
basic_http_css = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n" 
basic_http_png = "HTTP/1.1 200 OK\r\nContent-Type: image/png\r\n\r\n" 
basic_http_jpg = "HTTP/1.1 200 OK\r\nContent-Type: image/jpg\r\n\r\n"
basic_http_icon = "HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\n\r\n"
version = "0.1.5"
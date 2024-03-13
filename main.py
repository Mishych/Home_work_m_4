import socket
import json
from datetime import datetime
import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import threading

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        # print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        # print(data_parse)
        self.run_client(data_parse)
        self.send_response(302)
        
        self.send_header('Location', '/')
        self.end_headers()
        

    def run_client(self, data):
        ip = '127.0.0.1'
        port = 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = ip, port
        
        dat = str(data).encode()
        sock.sendto(dat, server)
        # print(f'Send data: {dat.decode()} to server: {server}')
        sock.close()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('contact.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_http(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

# серверна частина

UDP_IP = '127.0.0.1'
UDP_PORT = 5000

def append_to_json(data_dict):
    with open('storage/data.json', 'r+') as file:
        data = json.load(file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data[timestamp] = data_dict
        file.seek(0)
        json.dump(data, file, indent=4)

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data = data.decode()
            data_dict = {key: value for key, value in [el.split('=') for el in data.split('&')]}
            print(f'Received data: {data_dict} from: {address}')
            append_to_json(data_dict)
            print("Data appended to JSON file.")

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


server = threading.Thread(target=run_server, args=(UDP_IP, UDP_PORT))
http = threading.Thread(target=run_http)

if __name__ == '__main__':

    server.start()
    http.start()

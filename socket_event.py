# coding: utf-8
# author: elephanyu
import sys
import time
import socket
import traceback
from threading import Thread， Event

def now():
    now = time.time()
    return '%s.%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)), int(now % 1 * 1000))

# socket server
class myserver(Thread):
    def __init__(self, host='127.0.0.1', port=5000, time=1):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.time = time
        sock = self.get_sock()
        if sock:
            self.sock = sock
        else:
            print 'Server get sock err an dieded!'
            sys.exit(-1)
        self.exit = Event()
        print '%s Server init' % now()

    def stop(self):
        self.exit.set()

    def get_sock(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.bind((self.host, self.port))
            sock.listen(5)
            return sock
        except Exception:
            print traceback.format_exc()
            return None

    def run(self):
        while not self.exit.is_set():
            try:
                con, addr = self.sock.accept()
                if con:
                    con.send('Hello, i am server!')
                    time.sleep(self.time)
                    recv = con.recv(1024)
                    if recv:
                        print now() + ' ' + addr[0] + ' server accept: ' + str(recv)
            except Exception:
                print traceback.format_exc()
        print '%s Server nomal down!' % now()

# socket client
class myclient(Thread):
    def __init__(self, host='127.0.0.1', port=5000):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.exit = Event()
        print '%s Client init' % now()

    def stop(self):
        self.exit.set()

    def run(self):
        while not self.exit.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.host, self.port))
                sock.send('How are you, server?')
                recv = sock.recv(1024)
                if recv:
                    print now() + ' client accept: ' + str(recv)
                    sock.close()
            except Exception:
                print now() + ' ' + traceback.format_exc()
        print '%s Client normal down!' % now()

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    speed = 1
    rtime = 3
    server = myserver(host=host, port=port, time=speed)
    client = myclient(host=host, port=port)
    server.start()
    client.start()
    time.sleep(rtime)
    client.stop()
    server.stop()
    while True:
        time.sleep(0.5)
        s_status = server.is_alive()
        c_status = client.is_alive()
        print '%s Check server status: %s' % (now(), s_status)
        print '%s Check client status: %s' % (now(), c_status)
        if not s_status and not c_status:
            break

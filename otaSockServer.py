#! /usr/bin/env python
#! _*_ coding:utf-8 _*_

import os, logging, traceback
import socket, threading, json, base64
#
class skThread(threading.Thread):
    def __init__(self, sock, fdir):
        super(skThread, self).__init__()
        self.daemon = True
        self.sock = sock
        self.fdir = fdir
        self.c_name = None
        self.c_id = None
        self.c_version = None
    def run(self):
        try:
            (p_addr, p_port) = self.sock.getpeername()
            print("Connected from {0}:{1}".format(p_addr, p_port))
            self.sockf = self.sock.makefile(mode="rw")
            while True:
                line = self.sockf.readline().strip()
                if len(line) == 0:
                    break
                msg = json.loads(line)
                print("msg = {0}".format(repr(msg)))
                if msg["type"] == "hello":
                    self.c_name = msg["name"]
                    self.c_id = msg["id"]
                    self.c_version = msg["version"]
                    if type(self.c_name) is not unicode:
                        continue
                    if type(self.c_id) is not unicode:
                        continue
                    if type(self.c_version) is not int:
                        continue
                    self.hello(self.sockf)
                elif msg["type"] == "upgrade":
                    filen = msg["file"]
                    if type(filen) is not unicode:
                        continue
                    filename = self.find_filename(self.fdir, filen, self.c_version)
                    self.upgrade_filename(self.sockf, filename)
                    if filename is not None:
                        filepath = os.path.join(self.fdir, filename)
                        self.send_file(self.sockf, filepath)
        except:
            self.sock.close()
            print(traceback.format_exc())
        finally:
            print("Disconnected from {0}:{1}".format(p_addr, p_port))
    #
    def send_msg(self, sockf, msg):
        sockf.write("{0}\n".format(json.dumps(msg)))
        sockf.flush()
        #print("send_msg: {0}".format(repr(msg)))
    #
    def hello(self, sockf):
        msg = dict()
        msg["type"] = "hello"
        self.send_msg(sockf, msg)
    #
    def find_filename(self, fdir, filename, version):
        lf = list()
        for fn in os.listdir(fdir):
            if fn.endswith("_{0}".format(filename)):
                lf.append(fn)
        if len(lf) == 0:
            return None
        max_version = 0
        max_filename = None
        for f in lf:
            v = int(f.split("_{0}".format(filename))[0])
            if v > max_version:
                max_version = v
                max_filename = f
        if max_version > version and max_filename != None:
            return max_filename
        else:
            return None
    #
    def upgrade_filename(self, sockf, filename):
        msg = dict()
        msg["type"] = "upgrade"
        msg["step"] = "filename"
        msg["filename"] = filename
        self.send_msg(sockf, msg)
    #
    def upgrade_begin(self, sockf):
        msg = dict()
        msg["type"] = "upgrade"
        msg["step"] = "begin"
        self.send_msg(sockf, msg)
    #
    def upgrade_data(self, sockf, data):
        msg = dict()
        msg["type"] = "upgrade"
        msg["step"] = "data"
        msg["data"] = base64.b64encode(data)
        self.send_msg(sockf, msg)
    #
    def upgrade_finish(self, sockf):
        msg = dict()
        msg["type"] = "upgrade"
        msg["step"] = "finish"
        self.send_msg(sockf, msg)
    #
    def send_file(self, sockf, filepath):
        #print("filepath: {0}".format(filepath))
        with open(filepath, "rb") as f:
            self.upgrade_begin(sockf)
            while True:
                data = f.read(512)
                #print("len(data): {0}".format(len(data)))
                if len(data) == 0:
                    break
                self.upgrade_data(sockf, data)
            self.upgrade_finish(sockf)
    #
#
class ota():
    def __init__(self, port=9999):
        self.bdir = os.path.dirname(os.path.abspath(__file__))
        self.fdir = os.path.join(self.bdir, "files")
        self.sk = socket.socket()
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sk.bind(("0.0.0.0", port))
    def __call__(self):
        try:
            self.sk.listen(5)
            (l_addr, l_port) = self.sk.getsockname()
            print("Listen at {0}:{1}".format(l_addr, l_port))
            while True:
                try:
                    (conn, address) = self.sk.accept()
                    skThread(conn, self.fdir).run()
                except KeyboardInterrupt:
                    print("\rKeyboardInterrupt")
                    break
                except:
                    print(traceback.format_exc())
        finally:
            print("Finished with {0}:{1}".format(l_addr, l_port))
#
if __name__ == "__main__":
    app = ota(port=9009)
    app()
#

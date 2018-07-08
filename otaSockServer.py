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
                    rmsg = dict()
                    rmsg["type"] = "hello"
                    print("rmsg = {0}".format(repr(rmsg)))
                    self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                    self.sockf.flush()
                elif msg["type"] == "upgrade":
                    filen = msg["file"]
                    if type(filen) is not unicode:
                        continue
                    lf = list()
                    for f in os.listdir(self.fdir):
                        if f.endswith("_{0}".format(filen)):
                            lf.append(f)
                    if len(lf) == 0:
                        rmsg = dict()
                        rmsg["type"] = "upgrade"
                        rmsg["file"] = None
                        print("rmsg = {0}".format(repr(rmsg)))
                        self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                        self.sockf.flush()
                    else:
                        max_version = 0
                        max_filename = None
                        for f in lf:
                            v = int(f.split("_{0}".format(filen))[0])
                            if v > max_version:
                                max_version = v
                                max_filename = f
                        if max_version > self.c_version and max_filename != None:
                            with open(os.path.join(self.fdir, max_filename), "rb") as fo:
                                b = fo.read(512)
                                if len(b) == 0:
                                    rmsg = dict()
                                    rmsg["type"] = "upgrade"
                                    rmsg["file"] = max_filename
                                    rmsg["data"] = base64.b64encode(b)
                                    rmsg["next"] = False
                                    print("rmsg = {0}".format(repr(rmsg)))
                                    self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                                    self.sockf.flush()
                                    continue
                                while len(b) > 0:
                                    c = fo.read(512)
                                    if len(c) > 0:
                                        rmsg = dict()
                                        rmsg["type"] = "upgrade"
                                        rmsg["file"] = max_filename
                                        rmsg["data"] = base64.b64encode(b)
                                        rmsg["next"] = True
                                        print("rmsg = {0}".format(repr(rmsg)))
                                        self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                                        self.sockf.flush()
                                        b = c
                                    else:
                                        rmsg = dict()
                                        rmsg["type"] = "upgrade"
                                        rmsg["file"] = max_filename
                                        rmsg["data"] = base64.b64encode(b)
                                        rmsg["next"] = False
                                        print("rmsg = {0}".format(repr(rmsg)))
                                        self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                                        self.sockf.flush()
                                        b = c
                        else:
                            rmsg = dict()
                            rmsg["type"] = "upgrade"
                            rmsg["file"] = None
                            print("rmsg = {0}".format(repr(rmsg)))
                            self.sockf.write("{0}\n".format(json.dumps(rmsg)))
                            self.sockf.flush()
        except:
            self.sock.close()
            print(traceback.format_exc())
        finally:
            print("Disconnected from {0}:{1}".format(p_addr, p_port))
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

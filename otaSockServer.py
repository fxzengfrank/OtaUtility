#! /usr/bin/env python
#! _*_ coding:utf-8 _*_

import os, logging, traceback
import socket, threading, json
#
class skThread(threading.Thread):
    def __init__(self, sock):
        super(skThread, self).__init__()
        self.daemon = True
        self.sock = sock
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
        except:
            self.sock.close()
        finally:
            print("Disconnected from {0}:{1}".format(p_addr, p_port))
#
class ota():
    def __init__(self, port=9999):
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
                    skThread(conn).run()
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

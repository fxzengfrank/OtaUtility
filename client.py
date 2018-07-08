#! /usr/bin/env python
#! _*_ coding:utf-8 _*_

import socket, json
import logging, traceback

class client():
    def __init__(self, server="127.0.0.1", port=9999):
        self.server = server
        self.port = port
    def __call__(self):
        try:
            sock = socket.socket()
            sock.connect((self.server, self.port))
            (p_addr, p_port) = sock.getpeername()
            print("Connected to {0}:{1}".format(p_addr, p_port))
            sockf = sock.makefile(mode="rw")
            self.hello(sockf)
            while True:
                line = sockf.readline().strip()
                if len(line) == 0:
                    break
                msg = json.loads(line)
                print("msg = {0}".format(repr(msg)))
                if msg["type"] == "hello":
                    self.upgrade(sockf)
                elif msg["type"] == "upgrade":
                    pass
        except KeyboardInterrupt:
            print("\rKeyboardInterrupt")
            sock.close()
        except:
            sock.close()
            print(traceback.format_exc())
        finally:
            print("Disconnected with {0}:{1}".format(p_addr, p_port))
    def hello(self, sockf):
        msg = dict()
        msg["type"] = "hello"
        msg["name"] = "client"
        msg["id"] = "fake_id"
        msg["version"] = 0
        sockf.write("{0}\n".format(json.dumps(msg)))
        sockf.flush()
    def upgrade(self, sockf):
        msg = dict()
        msg["type"] = "upgrade"
        msg["file"] = "client.bin"
        sockf.write("{0}\n".format(json.dumps(msg)))
        sockf.flush()
#
if __name__ == "__main__":
    app = client(port=9009)
    app()

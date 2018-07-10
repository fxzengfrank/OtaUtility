#! /usr/bin/env python
#! _*_ coding:utf-8 _*_

import os, sys, socket, json, base64
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
        except socket.error as e:
            print("Socket Error")
            sys.exit(1)
        except:
            print(traceback.format_exc())
            sys.exit(1)
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
                    if msg["step"] == "filename":
                        new_filename = msg["filename"]
                    elif msg["step"] == "begin":
                        new_file = open(new_filename, "wb")
                    elif msg["step"] == "data":
                        new_data = base64.b64decode(msg["data"])
                        new_file.write(new_data)
                    elif msg["step"] == "finish":
                        new_file.close()
                        break
        except KeyboardInterrupt:
            print("\rKeyboardInterrupt")
            sock.close()
        except socket.error as e:
            print("Socket Error")
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

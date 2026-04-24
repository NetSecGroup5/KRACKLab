from models.msgs import *
from utils.ascii_prints import print_mitm

import socket
import pickle
import time

CLIENT = ['127.0.0.1', 5001]
AP = ['127.0.0.1', 5002]


class MStates():
    IDLE = 0
    READY = 1
    INSTALLED = 2

class MitMSocket():
    def __init__(self,addr,port):
        self._m = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._m.bind((addr, port))
        self._dst = []
        self._current_msg = None
        self._reply_msgs = []
        self._state = MStates.IDLE

    def send(self):

        match self._state:
            case MStates.IDLE | MStates.INSTALLED:
                if self._current_msg != None:
                    self.__send_msg(self._current_msg)
                    del self._current_msg
            case MStates.READY:
                msg = self._reply_msgs.pop(0)
                self.__send_msg(msg)
                time.sleep(0.5) # to make sure that the message arrives to the client
                msg = self._reply_msgs.pop(0)
                self.__send_msg(msg)
                self._state = MStates.INSTALLED


    def send_dass(self):
        msg = DassMSG()
        self._dst = CLIENT
        self.__send_msg(msg)

    def receive(self):
        self._m.settimeout(10)
        try:
            (msg,addr) = self.__get_msg()
            self._dst = CLIENT if self._dst is AP else AP
            match msg:
                case HandshakeMSG():
                    if msg.number < 4:
                        self._current_msg = msg
                    else:
                        if not any(isinstance(x, HandshakeMSG) for x in self._reply_msgs): # only add the first msg4
                            self._reply_msgs.append(msg)
                        else:
                            self._state = MStates.READY
                        
                case AssMSG() | CloseMSG():
                    self._current_msg = msg

                case EncMSG():
                    self._reply_msgs.append(msg)

                case _: # drop the packet
                    pass

        except socket.timeout:
            print("Nothing received\n Retrying...\n")

    def close(self):
        if len(self._dst) > 0 :
            msg = CloseMSG("Connection terminated by AP (MitM)")
            self.__send_msg(msg)
        self._m.close() 

    def __get_msg(self):
        data, addr = self._c.recvfrom(1024)
        msg = pickle.loads(data)
        return (msg,addr)
    
    def __send_msg(self, msg,dest):
        serialized_msg = pickle.dumps(msg)
        self._m.sendto(serialized_msg, (self._dst[0], self._dst[1]))


def main():
    M = MitMSocket('127.0.0.1', 5002)
    print_mitm()

    try:
        M.send_dass()

        while True:
            M.receive()
            M.send()

    except KeyboardInterrupt:
        print("Interruption detected by user.")
    finally:
        M.close()
        print("Simulation is terminated\n")

if __name__ == "__main__":
    main()
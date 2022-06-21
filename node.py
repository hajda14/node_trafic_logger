import json
import socket
from threading import Thread
import time 
import requests
from enum import Enum

class NODE_TYPE(Enum):
    MASTER = "MASTER"
    SLAVE = "SLAVE"

class Node():
    def __init__(self, node_type):
        self.node_type = node_type
        self.hostname = socket.gethostname()
        
        if node_type == NODE_TYPE.SLAVE:
            t = Thread(target=self.discovery,args=(self))
            t.start()
        elif node_type == NODE_TYPE.MASTER:
            t = Thread(target=self.broadcast)
            t.start()
            
    def waitForDevs(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            server_address = ('', 5621)
            print('starting up on {} port {}'.format(*server_address))
            sock.bind(server_address)
            while True:
                data, address = sock.recvfrom(1024)
                print(data,address)
                data = str(data, 'utf-8')
                if str(data)=="INTERNSHIP-DISCOVERY":
                    sock.close()
                    return address[0]
    
    def broadcast(self):
        while True:
            with socket.socket(socket.AF_INET, 
                        socket.SOCK_DGRAM, 
                    socket.IPPROTO_UDP) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.sendto(b'INTERNSHIP-DISCOVERY', ('255.255.255.255', 5621)) 
            time.sleep(5)


    
    def sendValues(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            data = {
                       "hostname":hostname,
                       "ip":local_ip,
                       "role":"slave"
                       }

            r = requests.post(f"http://{ip}:5620/management/update_inventory",data=data)
            print(r.status_code)
            
    def discovery(slave):
        while True:
            addr = slave.waitForDevs()
            print("found master at ",addr)
            slave.sendValues(addr)
            time.sleep(0.1)
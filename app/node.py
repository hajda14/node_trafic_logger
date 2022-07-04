import json
import socket
from threading import Thread
import time
from urllib import request 
import requests
from enum import Enum
from flask import Flask, request, jsonify, send_file
import platform
import psutil
import logging
import zlib
from datetime import date, datetime
import os

logging.basicConfig(filename="RESTlog.log",
                    filemode='a',
                    format='%(asctime)s%(msecs)03d+01:00 %(levelname)s %(hostname)s RID%(RID)s RestLogger: %(RID)s %(direction)s: %(body)s',
                    datefmt='%Y-%m-%d %H:%M:%S.',
                    level=logging.DEBUG)

logging.info("REST log")

logging.getLogger('werkzeug').disabled = True
logging.getLogger("requests").disabled = True
logging.getLogger("urllib3").disabled = True
logging.getLogger("requests").propagate = False
logging.getLogger("urllib3").propagate = False
logging.getLogger("werkzeug").propagate = False

logger = logging.getLogger('REST log')

class NODE_TYPE(Enum):
    MASTER = "MASTER"
    SLAVE = "SLAVE"


app=Flask(__name__)

inventory={
}
current_node=NODE_TYPE.SLAVE

def getNode():
    global current_node
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        return {
            "hostname":hostname,
            "ip":local_ip,
            "role":current_node.value
            }  

def get(*args,**kwargs):
    today = datetime.now()
    datetimer = today.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    node = getNode()
    rid = zlib.adler32(datetimer.encode())
    _url = kwargs['url'] if 'url' in kwargs else args[0]
    req_info=f"-X GET {_url}"
    print("-"*20,node["hostname"],"-"*20)
    logger.debug("GET",extra={"hostname":node['hostname'],"RID":rid, "direction":"SENT","body":req_info})
    response = requests.get(*args,**kwargs)
    
    try:
        resp_content = json.dumps(response.json())
    except ValueError:
        resp_content = {}
        
    res_info=f"{response.status_code}:{{\"data\":{resp_content}}}"
    logger.debug("POST",extra={"hostname":node['hostname'],"RID":rid, "direction":"RECEIVED","body":res_info})
    return response


def post(*args,**kwargs):
    today = datetime.now()
    datetimer = today.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    node = getNode()
    rid = zlib.adler32(datetimer.encode())
    _json = kwargs['json'] if 'json' in kwargs else ""
    _url = kwargs['url'] if 'url' in kwargs else args[0]
    req_info=f"-X POST {_url} -d \'{_json}\'"
    print("-"*20,node["hostname"],"-"*20)
    logger.debug("",extra={"hostname":node['hostname'],"RID":rid, "direction":"SENT","body":req_info})
    response = requests.post(*args,**kwargs)
    
    try:
        resp_content = json.dumps(response.json())
    except ValueError:
        resp_content = {}
        
    res_info=f"{response.status_code}:{{\"data\":{resp_content}}}"
    logger.debug("",extra={"hostname":node['hostname'],"RID":rid, "direction":"RECEIVED","body":res_info})
    return response


@app.route("/management/log/clearall", methods=["GET","POST"])
def clear_log_all():
    if current_node == NODE_TYPE.MASTER:  
        slaves = [slave for slave in inventory.values() if slave['role']==NODE_TYPE.SLAVE.value]
        results=[]
        for slave in slaves:
            resp = post(f"http://{slave['ip']}:5620/management/log/clearall")
            results.append(resp.json())
        result = getNode()
        try:
            with open("./RESTlog.log",'w') as f:
                pass
            res = "removed"
        except FileNotFoundError:
            res = "not removed"
        result['result'] = res
        results.append(result)
        return jsonify(results)
    elif current_node == NODE_TYPE.SLAVE:  
        result = getNode()
        try:
            with open("./RESTlog.log",'w') as f:
                pass
            res = "removed"
        except FileNotFoundError:
            res = "not removed"
        result['result'] = res
        return jsonify(result)
    
@app.route("/management/log/clear", methods=["GET","POST"])
def clear_log():
    if current_node == NODE_TYPE.MASTER:  
        results=[]
        result = getNode()
        try:
            with open("./RESTlog.log",'w') as f:
                pass
            res = "removed"
        except FileNotFoundError:
            res = "not removed"
        result['result'] = res
        results.append(result)
        return jsonify(results)
    
    return jsonify({"message":"NodeIsNotMasteError"})
    
@app.route('/management/log')
def send_report():      
    print(os.getcwd())
    return send_file('../RESTlog.log')

@app.route('/management/inventory')
def get_inventory():
    global inventory
    return jsonify(inventory)

@app.route("/management/update_inventory", methods=["POST"])
def update_inventory():
    global inventory
    if current_node == NODE_TYPE.MASTER:  
        data = request.json
        inventory[data['ip']]=data
        return jsonify(inventory)
    return jsonify({"message":"NodeIsNotMasteError"})

@app.route("/math/sum", methods=["GET","POST"])
def math_sum():
    if current_node == NODE_TYPE.MASTER:  
        to_sum=request.json
        slaves = [slave for slave in inventory.values() if slave['role']==NODE_TYPE.SLAVE.value]
        results=[]
        for slave in slaves:
            resp = post(f"http://{slave['ip']}:5620/math/sum",json=to_sum)
            results.append(resp.json())
            
        return jsonify(results)
    elif current_node == NODE_TYPE.SLAVE:  
        to_sum=request.json
        result = getNode()
        result['result'] = sum(to_sum)
        return jsonify(result)

@app.route("/system/system", methods=["GET","POST"])
def system_info():
    if current_node == NODE_TYPE.MASTER:  
        slaves = [slave for slave in inventory.values() if slave['role']==NODE_TYPE.SLAVE.value]
        results=[]
        for slave in slaves:
            resp = post(f"http://{slave['ip']}:5620/system/system")
            results.append(resp.json())
            
        return jsonify(results)
    elif current_node == NODE_TYPE.SLAVE:  
        result = getNode()
        result['result'] = platform.system()
        return jsonify(result)
    

@app.route("/disk/<function>", methods=["GET","POST"])
def disk_info(function):
    if current_node == NODE_TYPE.MASTER:  
        slaves = [slave for slave in inventory.values() if slave['role']==NODE_TYPE.SLAVE.value]
        results=[]
        for slave in slaves:
            resp = post(f"http://{slave['ip']}:5620/disk/{function}")
            results.append(resp.json())
            
        return jsonify(results)
    elif current_node == NODE_TYPE.SLAVE:  
        result = getNode()
        hdd = psutil.disk_usage('/')
        result['result']={}
        if(function=="total"):
            result['result']["total"] = f"{hdd.total / (2**30)}GiB"
            result['result']["total-ext"] = "GiB"
            return jsonify(result)
        elif(function=="used"):
            result['result']["used"] = f"{hdd.used / (2**30)}GiB"
            result['result']["used-ext"] = "GiB"
            return jsonify(result)
        elif(function=="free"):
            result['result']["free"] = f"{hdd.free / (2**30)}GiB"
            result['result']["free-ext"] = "GiB"
            return jsonify(result)
        else:
            result['result']["status"] = "command not found !"
            return jsonify(result)


class Node():
    def __init__(self, node_type):
        global inventory
        global current_node
        self.node_type = node_type
        self.hostname = socket.gethostname()
        
        if node_type == NODE_TYPE.SLAVE:
            print("Slave node", flush=True)
            current_node = NODE_TYPE.SLAVE
            t = Thread(target=self.discovery,args=(self,None))
            t.start()
            app.run(host="0.0.0.0",port=5620)
        elif node_type == NODE_TYPE.MASTER:
            print("Master node", flush=True)
            current_node = NODE_TYPE.MASTER
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                
                data = {
                        "hostname":hostname,
                        "ip":local_ip,
                        "role":NODE_TYPE.MASTER.value
                        }    
                        
                inventory[data['ip']]=data
            t = Thread(target=self.broadcast)
            t.start()
            app.run(host="0.0.0.0",port=5620)
    def waitForDevs(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            server_address = ('', 5621)
            print('starting up on {} port {}'.format(*server_address), flush=True)
            sock.bind(server_address)
            while True:
                data, address = sock.recvfrom(1024)
                print(data,address, flush=True)
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
                print("INTERNSHIP-DISCOVERY sent ...", flush=True)
            time.sleep(5)


    
    def sendValues(self, ip):
        global inventory
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            data = {
                       "hostname":hostname,
                       "ip":local_ip,
                       "role":NODE_TYPE.SLAVE.value
                       }
            url=f"http://{ip}:5620/management/update_inventory"
            print(url,flush=True)
            r = post(url,json=data)
            inventory=r.json()
            print (r.json(),flush=True)
            print(r.status_code, flush=True)
            
    def discovery(slave,test,test1):
        print("waiting for master Broadcast")
        while True:
            addr = slave.waitForDevs()
            print("found master at ",addr, flush=True)
            slave.sendValues(addr)
            time.sleep(0.1)
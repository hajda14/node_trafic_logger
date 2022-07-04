import pytest 
import requests
from masterip import get_master_ip 


def test_system():
     MASTER_IP=get_master_ip()
     response = requests.get(f"http://${MASTER_IP}:5620/system/system")
     for slave in response.json():
          assert slave['result'].lower() == "LINUX".lower()
     assert response.status_code == 200
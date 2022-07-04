import pytest 
import requests



def test_clear_all_logs():
     MASTER_IP=""
     with open("masterIP",'r') as f:
          MASTER_IP=f.read().strip()
     response = requests.get(f"http://{MASTER_IP}:5620/management/log/clearall")
     assert response.status_code == 200
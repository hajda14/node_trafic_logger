import pytest 
import requests
from masterip import get_master_ip 


def test_clear_all_logs():
     MASTER_IP=get_master_ip()
     response = requests.get(f"http://{MASTER_IP}:5620/management/log/clearall")
     assert response.status_code == 200
import pytest 
import requests



def test_system():
     response = requests.get("http://10.1.0.10:5620/system/system")
     for slave in response.json():
          assert slave['result'].lower() == "LINUX".lower()
     assert response.status_code == 200
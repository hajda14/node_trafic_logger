import pytest 
import requests



def test_clear_all_logs():
     response = requests.get("http://10.1.0.10:5620/management/log/clearall")
     assert response.status_code == 200
import pytest 
import requests
import time
from numpy import random as nprandom
import random
from masterip import get_master_ip 

def test_sum_numbers():
     MASTER_IP=get_master_ip()
     for i in range(random.randint(1000, 1500)):
          rand_array=nprandom.randint(100, size=(random.randint(1, 200))).tolist()
          response = requests.get(f"http://${MASTER_IP}:5620/math/sum",json=rand_array)
          for slave in response.json():
               assert slave['result'] == sum(rand_array)
          assert response.status_code == 200
          time.sleep(random.randint(0, 2))
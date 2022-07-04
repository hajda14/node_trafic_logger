import pytest 
import requests
import time
from numpy import random as nprandom
import random

def test_sum_numbers():
     
     for i in range(random.randint(1000, 1500)):
          rand_array=nprandom.randint(100, size=(5)).tolist()
          response = requests.get("http://10.1.0.10:5620/math/sum",json=rand_array)
          for slave in response.json():
               assert slave['result'] == sum(rand_array)
          assert response.status_code == 200
          time.sleep(random.randint(0, 2))
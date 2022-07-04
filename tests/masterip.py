def get_master_ip():
     with open("masterIP",'r') as f:
          return f.read().strip()
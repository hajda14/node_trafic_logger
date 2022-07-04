import socket, sys
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            server_address = ('', 5621)
            sock.bind(server_address)
            while True:
                data, address = sock.recvfrom(1024)
                data = str(data, 'utf-8')
                if str(data)=="INTERNSHIP-DISCOVERY":
                    sys.stdout.write(address[0])
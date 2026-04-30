import socket
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="327 Client")
    parser.add_argument("--localhost", help="connect to localhost", action="store_true")

    args = parser.parse_args()

    if args.localhost:
        server_ip = "127.0.0.1"
        server_port = 5000
    else:
        server_ip = str(input("server ip: "))
        server_port = int(input("server port: "))

    tcp_client(server_ip,server_port)

def tcp_client(server_ip:str, server_port:int):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"connecting to {server_ip}:{server_port}...")

        tcp_socket.connect((server_ip, server_port))
        
        print("connected")
        
        while True:
            data = input("input message (q to quit): ")
            if data == "q":
                print("quitting..")
                break

            tcp_socket.send(bytearray(data, encoding='utf-8'))

            server_response = tcp_socket.recv(1024)
            if not server_response:
                print("server disconnected")
                break

            message = server_response.decode('utf-8')
            print(f"server responded with: \"{message}\"")            
    except Exception as e:
        print(e)
    finally:
        tcp_socket.close()
        print("socket closed")
        
main()

import socket
import time

def main():
    #for quick testing purposes
    # server_ip = input("server ip: \n'd' for localhost\n")
    # if server_ip == 'd':
    #     server_ip = 'localhost'
    #     server_port = 1025
    # else:
    #     server_port = int(input("server port: "))
    server_ip = str(input("server ip: "))
    server_port = int(input("server port: "))

    print(f"debug; connecting to {server_ip}:{server_port}")

    tcp_client(server_ip,server_port)

def tcp_client(server_ip:str, server_port:int):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"connecting to {server_ip}:{server_port}...")
    tcp_socket.connect((server_ip, server_port))
    print("connected")

    try:
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

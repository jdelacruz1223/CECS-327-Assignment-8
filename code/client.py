import socket
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
        
        print("connected\n")

        while True:
            query_choice(tcp_socket)
            server_response(tcp_socket)          

    except Exception as e:
        print(e)
    finally:
        tcp_socket.close()
        print("socket closed")


def query_choice(tcp_socket):
    print("1. What is the average moisture inside our kitchen fridges in the past hours, week, and month?")
    print("2. What is the average water consumption per cycle across our smart dishwashers in the past hour, week and month?")
    print("3. Which house consumed more electricity in the past 24 hours, and by how much?")

    choice = input("Choose a query to run (q to quit): ")        

    match choice:
        case "1":
            print("Query 1 selected\n\n")
            query = str("What is the average moisture inside our kitchen fridges in the past hours, week, and month?").strip()
            tcp_socket.sendall(bytearray(query, encoding='utf-8'))
        case "2":
            print("Query 2 selected\n\n")
            query = str("What is the average water consumption per cycle across our smart dishwashers in the past hour, week and month?").strip()
            tcp_socket.sendall(bytearray(query, encoding='utf-8'))
        case "3":
            print("Query 3 selected\n\n")
            query = str("Which house consumed more electricity in the past 24 hours, and by how much?").strip()
            tcp_socket.sendall(bytearray(query, encoding='utf-8'))
        case "q":
            print("Quitting...")
            exit()
        case _:        
            print("Sorry, this query cannot be processed. Please try one of the supported queries. \n\n")
            tcp_socket.sendall(b'\x00')  # null byte for invalid response
        
def server_response(tcp_socket):
    server_response = tcp_socket.recv(1024) # receive server response
    
    if not server_response:
        print("server disconnected")
        return False

    message = server_response.decode('utf-8')
    print(f"\"{message}\"\n\n")            
    return True


main()

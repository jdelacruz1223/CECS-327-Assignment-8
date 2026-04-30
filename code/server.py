import socket
import psycopg
import argparse

connection_string = "postgresql://neondb_owner:npg_zlJOEZX04FoY@ep-empty-fire-ak1po874-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def main():
    parser = argparse.ArgumentParser(description="327 Server")
    parser.add_argument("--localhost", help="bind server to localhost", action="store_true")

    args = parser.parse_args()

    tcp_server(args)

def tcp_server(args):
    print("server start")
    
    # initialize db connection
    conn = psycopg.connect(connection_string)
    cur = conn.cursor()

    # cur.execute() # run queries
    # print(cur.fetchall()) # pring query to console

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    if args.localhost:
        port = 5000
        tcp_socket.bind(('localhost', port)) # attach socket to IP + port
    else:
        port = 1025
        tcp_socket.bind((hostname, port))

    tcp_socket.listen(5) # listen for clients
    print(f"listening.. on {ip_address}:{port}")

    try:
        while True:
            incoming_socket, incoming_address = tcp_socket.accept()
            print(f"{incoming_address} connected")

            try:
                while True:
                    print("while start")
                    
                    response = receive_data(incoming_socket)

                    send_data(incoming_socket, response)

            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                exit
            finally:
                incoming_socket.close()
                print("client socket closed")
    finally:
        tcp_socket.close()
        print("server socket closed")

def receive_data(socket):
    data = socket.recv(1024).decode('utf-8').strip() # receive data from client\

    if not data:
        print("client disconnected")
        return None
    
    print(f"received message: {data} \n\n")
    return data

def send_data(socket, data):
    data = data.upper()

    # handle data processing here
    
    socket.sendall(bytearray(data, encoding='utf-8'))

main()
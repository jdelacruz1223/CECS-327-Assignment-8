import socket
import psycopg

connection_string = "postgresql://neondb_owner:npg_zlJOEZX04FoY@ep-empty-fire-ak1po874-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def main():
    tcp_server()

def tcp_server():
    print("server start")
    
    # initialize db connection
    conn = psycopg.connect(connection_string)
    cur = conn.cursor()

    # cur.execute() # run queries
    # print(cur.fetchall()) # pring query to console

    port = 1025
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
    # tcp_socket.bind(('localhost', port)) # attach socket to IP + port
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
                    received_data = incoming_socket.recv(1024)
                    if not received_data:
                        print("client disconnected")
                        break

                    message = received_data.decode('utf-8')
                    response = message.upper()
                    print(f"received message: {message}")
                    incoming_socket.sendall(response.encode('utf-8'))
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

main()
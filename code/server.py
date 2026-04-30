import socket
import psycopg
import argparse
import json

connection_string = "postgresql://neondb_owner:npg_zlJOEZX04FoY@ep-empty-fire-ak1po874-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def main():
    parser = argparse.ArgumentParser(description="327 Server")
    parser.add_argument("--localhost", help="bind server to localhost", action="store_true")

    args = parser.parse_args()
    
    tcp_server(args)

def tcp_server(args):
    print("server start")
    
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
                    
                    received = receive_data(incoming_socket)

                    # handle queries with response input here
                    if received:
                        data = query_handler(incoming_socket, received)

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

def query_handler(socket, query):
    # handle queries here
    data = query

    # initialize db connection
    print("Connecting to database...")
    conn = psycopg.connect(connection_string)
    cur = conn.cursor()

    try:
        match query:
            case "What is the average moisture inside our kitchen fridges in the past hours, week, and month?":
                print("Query 1 selected\n\n")
                cur.execute("""
                    SELECT
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 hour' THEN moisture_val END) AS avg_last_hour,
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 week' THEN moisture_val END) AS avg_last_week,
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 month' THEN moisture_val END) AS avg_last_month
                    FROM (
                        SELECT
                            time,
                            (value)::float AS moisture_val
                        FROM table1_virtual, json_each_text(payload)
                        WHERE key ILIKE '%Fridge%'
                        AND key ILIKE '%Moisture%'
                    ) subquery
                    """)
                
                row = cur.fetchone()
                message = f"Hour: {row[0]},\nWeek: {row[1]},\nMonth: {row[2]}\n\n"

                socket.sendall(bytearray(message, encoding='utf-8'))

                
            case "What is the average water consumption per cycle across our smart dishwashers in the past hour, week and month?":
                print("Query 2 selected\n\n")
                cur.execute("""
                    SELECT 
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 hour' THEN consumption_val END) AS avg_last_hour,
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 week' THEN consumption_val END) AS avg_last_week,
                        AVG(CASE WHEN time >= NOW() - INTERVAL '1 month' THEN consumption_val END) AS avg_last_month
                    FROM (
                        SELECT
                            time,
                            (value)::float AS consumption_val
                        FROM table1_virtual, json_each_text(payload)
                        WHERE key ILIKE '%Dish%'
                    ) subquery
                    """)
                
                row = cur.fetchone()
                message = f"Hour: {row[0]},\nWeek: {row[1]},\nMonth: {row[2]}\n\n"

                socket.sendall(bytearray(message, encoding='utf-8'))

            case "Which house consumed more electricity in the past 24 hours, and by how much?":
                print("Not done yet! \n\n")
                # cur.execute("""
                    
                #     """)
                
                # row = cur.fetchone()
                # message = f"Hour: {row[0]},\nWeek: {row[1]},\nMonth: {row[2]}\n\n"
                # socket.sendall(bytearray(message, encoding='utf-8'))

            case _:
                print("Unknown query. Friendly message. \n\n")

        return data
        
    except Exception as e:
        print(e)
    finally:
        print("Closing database connection")
        cur.close()
        conn.close()

main()
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

    conn = psycopg.connect(connection_string)
    cur = conn.cursor()     

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
                    received = receive_data(incoming_socket)

                    # handle queries with response input here
                    data = query_handler(cur, received)
                    print("data: ", data)
                    if data:
                        incoming_socket.sendall(bytearray(data, encoding='utf-8'))

            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                exit()
            finally:
                incoming_socket.close()
                conn.close()
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

def query_handler(cur, query):
    # handle queries here
    data = query

    # initialize db connection
    print("Connecting to database...")

    # conn = psycopg.connect(connection_string)

    # print(conn.info.host)
    # print(conn.info.port)
    # print(conn.info.dbname)
    # print(conn.info.user)
    # print(conn.info.status)  # ConnStatus.OK or ConnStatus.BAD

    # cur = conn.cursor()

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
                message = f"Hour: {round(row[0], 2)},\nWeek: {round(row[1], 2)},\nMonth: {round(row[2], 2)}\n"

                print(f"returning: {message}")
                return message

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
                message = f"Hour: {round(row[0], 2)},\nWeek: {round(row[1], 2)},\nMonth: {round(row[2], 2)}\n"

                print(f"returning: {message}")
                return message

            case "Which house consumed more electricity in the past 24 hours, and by how much?":
                print("Not done yet! \n\n")
                return "Query 3 not yet implemented."
                # cur.execute("""
                    
                #     """)
                
                # row = cur.fetchone()
                # message = f"Hour: {row[0]},\nWeek: {row[1]},\nMonth: {row[2]}\n\n"
                # return message

            case _:
                message = "Sorry, this query cannot be processed. Please try one of the supported queries."
                return message

        return data
        
    except Exception as e:
        print(e)
    finally:
        print("Closing database connection")
        cur.close()

main()
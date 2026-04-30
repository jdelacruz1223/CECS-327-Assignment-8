import socket
import psycopg
import argparse

# First conn string: Justin (table1_virtual)
# Second conn string: Anna (IoTData_virtual)
connection_string = ["postgresql://neondb_owner:npg_zlJOEZX04FoY@ep-empty-fire-ak1po874-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
                     "postgresql://neondb_owner:npg_KQaA0lIWvBN1@ep-ancient-resonance-an7pgvan-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"]

# Main function
def main():
    parser = argparse.ArgumentParser(description="327 Server")
    parser.add_argument("--localhost", help="bind server to localhost", action="store_true")

    args = parser.parse_args()
    
    tcp_server(args)


# TCP Server function
def tcp_server(args):
    print("server start")
    
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    db_resources = init_database_connection()
    if not db_resources: return # if db connection failed, exit
    conn1, conn2, cur1, cur2, table1_name, table2_name = db_resources

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
                    if not received: break # client disconnected, break to accept new clients

                    # handle queries with response input here
                    data = query_handler(cur1, cur2, table1_name, table2_name, received)
                    print("data: ", data)
                    if data:
                        incoming_socket.sendall(bytearray(data, encoding='utf-8'))
            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                exit()
            finally:
                incoming_socket.close()
                print("Client socket closed")
    finally:
        print("Closing database connection")
        cur1.close()
        cur2.close()
        conn1.close()
        conn2.close()
        tcp_socket.close()
        print("Server socket closed")

# Initializing database connection
def init_database_connection():
    # initialize db connection
    print("Connecting to databases...")
    try:
        conn1 = psycopg.connect(connection_string[0])
        conn2 = psycopg.connect(connection_string[1])

        cur1 = conn1.cursor()
        cur2 = conn2.cursor()

        cur1.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%table1_virtual%'
            LIMIT 1
        """)
        table1_name = cur1.fetchone()[0]
        print("table 1 name: ", table1_name)

        cur2.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%IoTData_virtual%'
            LIMIT 1
        """)
        table2_name = cur2.fetchone()[0]
        print("table 2 name: ", table2_name)

        print("Databases connected!")
        return conn1, conn2, cur1, cur2, table1_name, table2_name
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit()


# TCP Client function
def receive_data(socket):
    data = socket.recv(1024).decode('utf-8').strip() # receive data from client\

    if not data:
        print("client disconnected")
        return None
    
    print(f"received message: {data} \n\n")
    return data


# Query handler function for all 3 queries
def query_handler(cur1, cur2, table1_name, table2_name, query):
    # handle queries here
    data = query

    try:
        match query:
            # QUERY 1: Moisture in fridges (from both tables)
            case "What is the average moisture inside our kitchen fridges in the past hours, week, and month?":
                print("Query 1 selected\n\n")
                cur1.execute(moisture_query(table1_name))
                row1 = cur1.fetchone()
                print("row1: ", row1)

                cur2.execute(moisture_query(table2_name))
                row2 = cur2.fetchone()
                print("row2: ", row2)
                
                avg_hour  = safe_avg(row1[0], row2[0])
                avg_week  = safe_avg(row1[1], row2[1])
                avg_month = safe_avg(row1[2], row2[2])

                message = f"Hour: {round(avg_hour, 2)}\nWeek: {round(avg_week, 2)}\nMonth: {round(avg_month, 2)}\n"
                return message

            # QUERY 2: Water consumption in dishwashers (from both tables)
            case "What is the average water consumption per cycle across our smart dishwashers in the past hour, week and month?":
                print("Query 2 selected\n\n")
                cur1.execute(water_consumption_query(table1_name))
                row1 = cur1.fetchone()

                cur2.execute(water_consumption_query(table2_name))
                row2 = cur2.fetchone()

                avg_hour  = safe_avg(row1[0], row2[0])
                avg_week  = safe_avg(row1[1], row2[1])
                avg_month = safe_avg(row1[2], row2[2])

                message = f"Hour: {round(avg_hour, 2)}\nWeek: {round(avg_week, 2)}\nMonth: {round(avg_month, 2)}\n"

                return message

            # QUERY 3: Electricity consumption in houses (compare both tables)
            case "Which house consumed more electricity in the past 24 hours, and by how much?":
                print("Query 3 selected\n\n")

                # House 1
                cur1.execute(electricity_consumption_query(table1_name))
                row1 = cur1.fetchone()

                # House 2
                cur2.execute(electricity_consumption_query(table2_name))
                row2 = cur2.fetchone()

                diff = abs(row1[0] - row2[0])
                chosen_house = "House 1" if row1[0] > row2[0] else "House 2"
                return f"{chosen_house} consumed more electricity by {diff:.2f} kWh in the past 24 hours."

            case _:
                message = "Sorry, this query cannot be processed. Please try one of the supported queries."
                return message

        return data
        
    except Exception as e:
        print(e)
        return "An error occurred while processing the query."

# Logic for queries
# Moisture
def moisture_query(table_name):
    return f"""
        SELECT
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 hour' THEN moisture_val END) AS avg_last_hour,
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 week' THEN moisture_val END) AS avg_last_week,
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 month' THEN moisture_val END) AS avg_last_month
        FROM (
            SELECT
                time,
                (value)::float AS moisture_val
            FROM {table_name}, json_each_text(payload)
            WHERE key ILIKE '%Fridge%'
            AND key ILIKE '%Moisture%'
        ) subquery
    """

# Water consumption
def water_consumption_query(table_name):
    return f"""
        SELECT 
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 hour' THEN consumption_val END) AS avg_last_hour,
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 week' THEN consumption_val END) AS avg_last_week,
            AVG(CASE WHEN time >= NOW() - INTERVAL '1 month' THEN consumption_val END) AS avg_last_month
        FROM (
            SELECT
                time,
                (value)::float AS consumption_val
            FROM {table_name}, json_each_text(payload)
            WHERE key ILIKE '%Dish%'
        ) subquery
    """
    
# Electricity consumption
def electricity_consumption_query(table_name):
    return f"""
        SELECT 
            SUM((value)::float)
        FROM
            {table_name},
            json_each_text(payload)
        WHERE
            (key ILIKE '%Ammeter%'
            OR key ILIKE '%sd_power_current%'
            OR key ILIKE '%power_current%')
            AND time >= NOW() - INTERVAL '24 hours'
    """


def safe_avg(a, b):
    values = [v for v in [a, b] if v is not None]
    return sum(values) / len(values) if values else None

main()
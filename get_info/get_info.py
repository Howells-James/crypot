import requests
import json
import pyodbc
import datetime
import time
import socket
server = socket.gethostname()
server += "\\SQLEXPRESS"
connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')

sleep_time = 15

#this script needs to be run continuesly in the background. It makes the api calls that collect price and time information 
#for each currency.


class dataStruct():
    symbol = ''
    timestamp = ''
    price = ''
    def __init__(self, symbol, timestamp, price):
        self.symbol = symbol
        self.timestamp = timestamp
        self.price = price

def get_gmt_time():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

def get_info():
    global sleep_time
    sleep_increment = 1
    while True:
        try:
            req = requests.get("https://data.messari.io/api/v1/assets?fields=id,slug,symbol,metrics/market_data/price_usd")
            market_data = json.loads(req.text)
            set_connection_status(1)
            sleep_increment = 1
            #print(json.loads(req.text)) #print raw response
            for x in range(0, 20):
                timestamp = market_data["status"]["timestamp"]
                timestampUTC = timestamp.replace('Z', 'UTC')
                symbol = market_data["data"][x]["symbol"]
                btc_price = market_data["data"][x]["metrics"]["market_data"]["price_usd"]
                data = dataStruct(symbol, timestampUTC, btc_price) 
                #printData(data)
                #dataArray.append(data)
                write_to_db(data)  
        except Exception:
            set_connection_status(0)
            print("connection error, backing off for " + str(sleep_time + sleep_increment) + " seconds")
            time.sleep(sleep_time + sleep_increment)
            sleep_increment = sleep_increment + 9
            continue      
        print("Tick")
        time.sleep(sleep_time)
        print('Tock')

def set_connection_status(status):
    global connection
    cursor = connection.cursor()
    query = ("update connection_status set current_connection = ? where sn = 1")
    cursor.execute(query, status)
    connection.commit()

def printData(data):
    print(str(data.symbol) + '\n' + str(data.timestamp) + '\n' + str(data.price))

def write_to_file(data):
    file = open('Data.txt', 'a')
    for item in data:
        file.write(str(item) + '\n')

def write_to_db(data):
    global connection
    cursor = connection.cursor()
    query = ("(select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = 'dbo' and TABLE_NAME = ?)")
    cursor.execute(query, data.symbol)
    exists = False
    for item in cursor:
        if item[0] == data.symbol:
            exists = True
    if exists:
        query = ("insert into crypot.dbo."+data.symbol+" (price, time) values (?, ?)")
        values = [data.price, data.timestamp]
        cursor.execute(query, values)
        connection.commit()
    else:
        print("Createing new table for: " + data.symbol)
        query = ("create table crypot.dbo."+data.symbol+" (price float, time nchar(255))")
        cursor.execute(query)
        connection.commit() 
    connection.commit()

    #query = ("insert into crypot.dbo."+data.symbol+" (price, time) values (?, ?)")
    #values = [data.price, data.timestamp]
    #cursor.execute(query, values)
    #connection.commit()

#test_struct = dataStruct('PISS', get_gmt_time(), 504.234) 
get_info()

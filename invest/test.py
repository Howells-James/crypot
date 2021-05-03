import requests
import pyodbc
import datetime
import time
import random 
import invest as inv
import socket
import datetime 

server = socket.gethostname()
server += "\\SQLEXPRESS"

def going_up(coin):
    current_value = inv.get_current_price_from_db(coin)
    now = datetime.datetime.now()
    yesterday = (now - datetime.timedelta(hours=24))
    prev_value = inv.get_coin_value_at_time(coin, str(yesterday))
    total_diff = prev_value - current_value #positive if value gone down, negative if value gone up, same if no change 
    print(total_diff)
    if total_diff > 0:
        return -1
    elif total_diff == 0:
        return 0
    else:
        return 1

going_up('BTC')
#import invest as inv
import requests
import pyodbc
import datetime
import time
import random 
import invest as inv
import socket

server = socket.gethostname()
server += "\\SQLEXPRESS"

def going_up(coin):
    #get current value
    current_value = inv.get_current_price_from_db(coin)
    #get value from last update
    prev_value = inv.get_previous_price_from_db(coin)
    total_diff = prev_value - current_value #positive if value gone down, negative if value gone up, same if no change 
    if total_diff > 0:
        return -1
    elif total_diff == 0:
        return 0
    else:
        return 1

def greater_than_buy(coin):
    current_value = inv.get_holdings_value(coin)
    total_spent_since_last_zero = inv.get_spend_since_zero(coin)
    if current_value > total_spent_since_last_zero:
        return 1
    else:
        return -1

def get_connection_status():
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    #this query needs to sum up number of units involved in buy events in table
    query = ("select current_connection from connection_status where sn = 1")
    cursor.execute(query)
    total = 0 #default to no connection
    for item in cursor:
        total = item[0]
    connection.commit()
    return total

def main_loop():
    list_of_coins = inv.get_all_stored_coins()
    list_to_not_buy = []
    while True:
        if get_connection_status() == 1:
            for item in list_of_coins:
                if going_up(item) > 0:
                    if item not in list_to_not_buy:
                        current_money = inv.get_USD() / 2
                        num_coin_types = len(list_of_coins)
                        money_to_invest = current_money / num_coin_types
                        inv.buy_in_USD(money_to_invest, inv.get_gmt_time(), item)
                        print("Bought " + item)
                elif going_up(item) == 0:
                    print("holding "+ item)
                else:
                    if greater_than_buy(item) < 0:
                        print("selling " + item)
                        num_coin = inv.get_current_holdings(item)
                        if num_coin > 0:
                            inv.sell_sell_sell(num_coin, inv.get_gmt_time(), item)
                        else:
                            print("no "+item+" to sell")
                        if item in list_to_not_buy:
                            list_to_not_buy.remove(item)
                            print(item + " recovered, putting it back on the list")
                    else:
                        if item not in list_to_not_buy:
                            list_to_not_buy.append(item)
                            print("not buying anymore "+ item)
                        print("holding " + item)
            time.sleep(20)
        else:
            print("no connection, sleeping for 30 sec")
            time.sleep(30)



main_loop()
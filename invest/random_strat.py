#import invest as inv
import requests
import pyodbc
import datetime
import time
import random 
import invest as inv

def main():
    num_coin_types = len(inv.get_all_stored_coins())
    usd_amount = inv.get_USD()
    usd_for_each_coin = usd_amount / num_coin_types
    while True:
        for coin in inv.get_all_stored_coins():
            choice = random.randint(0,2) # 0 = hold, 1 = buy, 2 = sell
            if choice == 0:
                print("Coin: " + coin + " Action: Hold")
            elif choice == 1:
                #try to buy random amount of coin
                print("Coin: " + coin + " Action: Buy")
                inv.buy_in_USD(float(inv.get_USD() / random.randint(1, 10)), inv.get_gmt_time() ,coin)
            elif choice == 2:
                #try to sell random amount of coin
                if inv.get_current_holdings(coin) > 0:
                    print("Coin: " + coin + " Action: Sell")
                    inv.sell_sell_sell(float(inv.get_current_holdings(coin)) / random.randint(1, 10), inv.get_gmt_time(), coin)
                else:
                    print("can't sell what we dont own")
        time.sleep(10)

main()
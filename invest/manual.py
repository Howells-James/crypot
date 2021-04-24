import requests
import pyodbc
import datetime
import time
import pyinputplus as inp
import invest as inv
import sys
sys.path.append('../')
import graph_coin as gc

def main():
    while(True):
        action = input("waiting for input...")
        if action == 'buy':
            amount = inp.inputNum("amount? (in USD) $")
            coin = input("symbol? ")
            inv.buy_in_USD(amount, inv.get_gmt_time(), str.upper(coin))
        elif action == 'sell':
            amount = inp.inputNum("amount? ")
            coin = input("symbol? ")
            inv.sell_sell_sell(amount, inv.get_gmt_time(), str.upper(coin))
        elif action == 'report':
            report(input("type? "))
        elif action == 'restart':
            inv.reset_investment_tables()
        elif action == 'help':
            help()
        elif action == 'exit':
            break

def report(type_of_report):
    if type_of_report == 'single':
        coin = input("symbol? ")
        if inv.coin_exists(str.upper(coin)):
            current_coins = inv.get_all_stored_coins()
            total_gain = 0
            current_value = inv.get_holdings_value(str.upper(coin)) 
            current_gain = inv.get_current_gain(coin)
            total_gain += current_gain
            print("Total current value of " + coin + " is $" + str(current_value))
            print("Total spent on coin $" + str(inv.get_cumulative_total(coin)))
            print("Total gain on coin is: $" + str(current_gain))
            print("Total coin owned: " + str(inv.get_current_holdings(coin)) +"\n")
        else:
            print("No coin with that symbol")
    elif type_of_report == 'all':
        current_coins = inv.get_all_stored_coins()
        total_gain = 0
        for coin in current_coins:
            if inv.is_in_table(coin):
                current_value = inv.get_holdings_value(str.upper(coin)) 
                current_gain = inv.get_current_gain(coin)
                total_gain += current_gain
                print("Total current value of " + coin + " is $" + str(current_value))
                print("Total spent on coin $" + str(inv.get_cumulative_total(coin)))
                print("Total gain on coin is: $" + str(current_gain))
                print("Total coin owned: " + str(inv.get_current_holdings(coin)) +"\n")
        print("Sum total gain $" + str(total_gain))
    elif type_of_report == 'market':
        current_coins = inv.get_all_stored_coins()
        for coin in current_coins:
            market_value = inv.get_current_price_from_db(coin)
            print(coin + " : $" + str(market_value))
    elif type_of_report == 'money':
        current_balance = inv.get_USD()
        print("current USD $" + str(current_balance))
    elif type_of_report == 'graph':
        coin = input("symbol? ")
        gc.main(coin)

def help():
    print("actions: buy, sell, report, exit, restart")
    print("buy: starts a buy process, you will need to enter $ amount, and symbol of coin")
    print("sell: starts a sell process, you will need to enter a coin amount, and symbol of coin")
    print("report: single, all, money, market")
    print(" -- single: prints report for a single owned coin type")
    print(" -- all: prints report for all owned coing")
    print(" -- money: prints amount of USD you have left")
    print(" -- market: prints current market data, market data refreshes every 20 second")
    print("restart: clears all investments, and resets USD amount to $100")
    print("exit: exit investor program, data collector will still be running")

main()
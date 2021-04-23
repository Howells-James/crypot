import invest as inv
import time

amount_to_buy = 10

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def test_buy(symbol):
    inv.reset_investment_tables()
    global amount_to_buy
    inv.buy_in_USD(amount_to_buy, inv.get_gmt_time(), symbol)
    current_num_btc = inv.get_current_holdings(symbol)
    translate_to_usd_btc = current_num_btc * inv.get_current_price_from_db(symbol)
    if translate_to_usd_btc == amount_to_buy:
        print(f"{bcolors.OKGREEN}Buying coin passed{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Buying coin failed{bcolors.ENDC}")

def test_sell_in_coin(symbol):
    test_buy(symbol) #get $10 of symbol
    num_units = inv.get_current_holdings(symbol)
    inv.sell_sell_sell(num_units, inv.get_gmt_time(), symbol)
    current_num_coin = inv.get_current_holdings(symbol)
    cumu_gain = inv.get_current_gain(symbol)
    if cumu_gain == 0:
        print(f"{bcolors.OKGREEN}Selling coin cumu_gain back to zero passed{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Selling coin cumu_gain back to zero failed{bcolors.ENDC}")  
    if current_num_coin == 0:
        print(f"{bcolors.OKGREEN}Selling coin units back to zero passed{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Selling coin units back to zero failed{bcolors.ENDC}")        

def test_num_in_current_holdings(symbol):
    try:
        num = len(inv.get_all_stored_coins())
    except Exception:
        if num == 1:
            print(f"{bcolors.OKGREEN}num in current_holdings is 1{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}num in current_holdings is not 1{bcolors.ENDC}")   

def test_usd_amount():
    global amount_to_buy
    inv.reset_investment_tables()
    current_balance = inv.get_USD()
    if current_balance == 100:
        print(f"{bcolors.OKGREEN}current balance 100 after reset{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}current balance not 100 after reset{bcolors.ENDC}")   
    test_buy('BTC')
    current_balance = inv.get_USD()
    if current_balance == 100 - amount_to_buy:
        print(f"{bcolors.OKGREEN}current balance ok after buy{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}current balance not ok after buy{bcolors.ENDC}")

def test_partial_sell_in_coin(symbol):
    inv.reset_investment_tables()
    test_buy(symbol) #get $10 of symbol
    num_coin_units = inv.get_current_holdings(symbol) / 2
    inv.sell_sell_sell(num_coin_units, inv.get_gmt_time(), symbol) #sell half coins
    current_num_coin = inv.get_current_holdings(symbol)
    cumu_gain = inv.get_current_gain(symbol)
    current_num_coin = inv.get_current_holdings(symbol)
    if current_num_coin == num_coin_units:
        print(f"{bcolors.OKGREEN}Selling half coin units passed{bcolors.ENDC}")
        ### now need to test for cumu_spend_since_zero
        time.sleep(20) #need to wait for market data to change price
        test_cumu_spend_since_zero(symbol)
    else:
        print(f"{bcolors.FAIL}Selling coin units back to zero failed{bcolors.ENDC}")   

def test_cumu_spend_since_zero(symbol):
    num_coin_units = inv.get_current_holdings(symbol)
    inv.sell_sell_sell(num_coin_units, inv.get_gmt_time(), symbol) #sell rest of coins
    ##current historic should not be zero
    cumu_gain = inv.get_current_gain(symbol)
    if cumu_gain != 0:
        print(f"{bcolors.OKGREEN}Selling coin cumu_gain back to zero passed{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Selling coin cumu_gain back to zero failed (is collection turned on!!!){bcolors.ENDC}") 
    #should be zero
    cumu_gain_curr = inv.get_spend_since_zero(symbol)
    if cumu_gain_curr == 0:
        print(f"{bcolors.OKGREEN}Selling coin to zero cumu_gain_to_zero passed{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Selling coin to zero cumu_gain_to_zero failed (is collection turned on!!!){bcolors.ENDC}") 


def main():
    inv.reset_investment_tables()
    test_buy('BTC')
    test_sell_in_coin('BTC')
    test_num_in_current_holdings('BTC')
    test_usd_amount()
    test_partial_sell_in_coin('BTC')
    inv.reset_investment_tables()


main()
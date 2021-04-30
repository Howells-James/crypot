import requests
import pyodbc
import datetime
import time
import pyinputplus as inp
import socket

server = socket.gethostname()
server += "\\SQLEXPRESS"
print("Connection String: " + 'Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')

def get_gmt_time():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

### HELPER FUNCTIONS

#deletes all information from the investment tables
def reset_investment_tables():
    global connection
    cursor = connection.cursor()
    delete_buy_events = ("delete from investment_buy_events")
    delete_sell_events = ("delete from investment_sell_events")
    delete_current_holdings = ("delete from current_holdings")
    resett_usd_amount = ("update USD set units = 100 where sn = 1")
    cursor.execute(delete_buy_events)
    cursor.execute(delete_sell_events)
    cursor.execute(delete_current_holdings)
    cursor.execute(resett_usd_amount)
    connection.commit()

#delete all information from all tables TODO


#returns true if a table exists for the symbol
def coin_exists(symbol):
    global connection
    cursor = connection.cursor()
    query = ("(select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = 'dbo' and TABLE_NAME = ?)")
    cursor.execute(query, symbol)
    exists = False
    for item in cursor:
        if item[0] == symbol:
            exists = True
    return exists

#returns true if symbol is in current_holdings
def is_in_table(symbol):
    global connection
    cursor = connection.cursor()
    query = ("select count(1) from crypot.dbo.current_holdings where symbol = ?") 
    cursor.execute(query, symbol)
    result = -1000
    for item in cursor:
        result = item[0]
    if result == 1:
        return True
    else:
        return False

### BUY AND SELL

#Params: the amount of coin you want to buy, the current time, the coin you want
def buy_buy_buy(num_units, time, symbol):
    if num_units <= 0:
        print("can't buy 0 coins")
        return
    if coin_exists(symbol):
        global connection
        cursor = connection.cursor()
        query = ("insert into crypot.dbo.investment_buy_events (units, time_aquired, transaction_id, symbol, price_when_aquired) values (?,?,?,?,?)") 
        price_when_aquired = get_current_price_from_db(symbol)
        transaction_id = int(get_transaction_number('buy')) + 1
        values = (num_units, time, transaction_id, symbol, price_when_aquired)
        cursor.execute(query, values)
        connection.commit()
        update_current_holdings(symbol)
        update_cumulative_spent(num_units, symbol, False)
        print("bought "+ str(num_units) + " of " + str(symbol) +" at "+ str(price_when_aquired) + " per coin, total value: $"+ str(num_units * price_when_aquired))
    else:
        print("no such coin, not buying anything")

# buys the amount of coin you can get at the current price for the usd amount passed in
def buy_in_USD(usd_amount, time, symbol):
    if usd_amount <= 0:
        print("cant buy $0 worth of coin")
        return
    current_balance = get_USD()
    if current_balance >= usd_amount:
        current_price = get_current_price_from_db(symbol)
        total_to_buy = usd_amount / current_price
        buy_buy_buy(total_to_buy, time, symbol)
        sell_USD(usd_amount)
    else:
        print("You only have $" + str(current_balance))

#sells USD for coins, used in buy_buy_buy
def sell_USD(amount):
    global connection
    cursor = connection.cursor()
    query = ("update crypot.dbo.USD set units = (select units from crypot.dbo.USD where sn = 1) - ?")
    cursor.execute(query, amount)
    connection.commit()

#creates a sell event in the investment_sell_events table. this is used to calculate total current holdings of a coin
#also needs to transfer all current value of sold coin to USD table
def sell_sell_sell(num_units, time, symbol):
    if num_units <= 0:
        print("Fuck off")
        return
    current_holdings = get_current_holdings(symbol)
    if float(num_units) > float(current_holdings):
        print("not enough to sell that much " + symbol)
    else:
        global connection
        cursor = connection.cursor()
        transaction_id = int(get_transaction_number('sell')) + 1
        current_price = get_current_price_from_db(symbol)
        query = ("insert into crypot.dbo.investment_sell_events (units, time_sold, transaction_id, symbol, price_when_sold) values (?,?,?,?,?)") 
        values = (num_units, time, transaction_id, symbol, current_price)
        cursor.execute(query, values)
        connection.commit()
        update_current_holdings(symbol)
        to_zero = get_sum_buy_events(symbol) - get_sum_sell_events(symbol)
        if to_zero == 0:
            update_cumulative_spent(-num_units, symbol, True)
        else:
            update_cumulative_spent(-num_units, symbol, False)
        sold_value = num_units * current_price
        buy_USD(sold_value)

#used in sell_sell_sell, adds the value of sold coin to the USD table
def buy_USD(amount):
    global connection
    cursor = connection.cursor()
    query = ("update crypot.dbo.usd set units = (select units from crypot.dbo.usd where sn = 1) + ? where sn = 1")
    cursor.execute(query, amount)
    connection.commit()

### ALL UPDATE FUCNTIONS HERE

#updates current_holdings table with the values of coins bought at the time of buy event
def update_cumulative_spent(num_units, symbol, to_zero):
    global connection
    cursor = connection.cursor()
    query = ("update crypot.dbo.current_holdings set cumulative_spending_historic = (select cumulative_spending_historic from current_holdings where symbol = ?) + ? where symbol = ?;")
    query2 = ("update crypot.dbo.current_holdings set cumulative_spending_since_zero = (select cumulative_spending_since_zero from current_holdings where symbol = ?) + ? where symbol = ?;")
    current_spend = num_units * get_current_price_from_db(symbol)
    values = (symbol, current_spend, symbol)
    cursor.execute(query, values)
    if not to_zero:
        cursor.execute(query2, values)
    connection.commit()

#takes in symbol and updates the current_holdings table based on what is in buy_events and sell_events
def update_current_holdings(symbol):
    global connection
    cursor = connection.cursor()
    #this will always fuck up the since zero measure
    current_holdings = get_sum_buy_events(symbol) - get_sum_sell_events(symbol)
    if is_in_table(symbol):
        query = ("update crypot.dbo.current_holdings set current_holdings = "+str(current_holdings)+" where symbol = ?;")
        cursor.execute(query, symbol)
        if current_holdings == 0:
            query = ("update crypot.dbo.current_holdings set cumulative_spending_since_zero = 0 where symbol = ?;")
            cursor.execute(query, symbol)
        connection.commit()
    else:
        query = ("insert into crypot.dbo.current_holdings (current_holdings, symbol, cumulative_spending_historic, cumulative_spending_since_zero) values (?,?, 0, 0);")
        values = (current_holdings, symbol)
        cursor.execute(query, values)
        connection.commit()

### ALL REPORT FUCNTIONS BELOW HERE

def get_spend_since_zero(symbol):
    global connection
    cursor = connection.cursor()
    query = ("select cumulative_spending_since_zero from current_holdings where symbol = ?")
    amount = -1
    cursor.execute(query, symbol)
    for item in cursor:
        amount = item[0]
    connection.commit()
    return amount

#returns current amount of USD 
def get_USD():
    global connection
    cursor = connection.cursor()
    query = ("select units from crypot.dbo.USD where sn = 1")
    cursor.execute(query)
    current_amount = 0
    for item in cursor:
        current_amount = item[0]
    connection.commit()
    return current_amount

#returns list of all current tables for coin values
def get_all_stored_coins():
    global connection
    cursor = connection.cursor()
    query = ("select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = 'dbo'")
    cursor.execute(query)
    #exclude these tables from returned list. Need to deal with USD table differently 
    investment_tables = ('current_holdings', 'investment_buy_events', 'investment_sell_events', 'USD', 'connection_status', 'sysdiagrams')
    coin_tables = []
    for item in cursor:
        if item[0] not in investment_tables:
            coin_tables.append(item[0])
    return coin_tables


#returns the current # of coins held for a coin type designated by Symbol parameter
def get_current_holdings(symbol):
    global connection
    cursor = connection.cursor()
    #this query needs to sum up number of units involved in buy events in table
    query = ("select current_holdings from crypot.dbo.current_holdings where symbol = ?;")
    cursor.execute(query, symbol)
    current = -100
    for item in cursor:
        current = item[0]
    if current >= 0:
        return current
    else:
        return 0

#returns current total spent on the symbol
def get_cumulative_total(symbol):
    global connection
    cursor = connection.cursor()
    query = ("select cumulative_spending_historic from crypot.dbo.current_holdings where symbol = ?") 
    cursor.execute(query, symbol)   
    current_holding = -1
    for item in cursor:
        current_holding = item[0]
    connection.commit()
    return current_holding

#returns the current USD value of symbol, if table exsists for symbol
def get_holdings_value(symbol):
    update_current_holdings(symbol) # make sure this is accurate
    current_price = get_current_price_from_db(symbol)
    current_holdings = get_current_holdings(symbol)
    current_value = current_price * current_holdings
    return current_value

#returns the latest entry in the coin table specified by the Symbol parameter
def get_current_price_from_db(symbol):
    global connection
    cursor = connection.cursor()
    query = ("SELECT TOP 1 price FROM crypot.dbo."+symbol+" ORDER BY time DESC") #get latest entry in table #TODO ????????
    cursor.execute(query)
    for item in cursor:
        return item[0]
    connection.commit()

# Returns second most recent entry in table
def get_previous_price_from_db(symbol):
    global connection
    cursor = connection.cursor()
    query = ("SELECT price FROM crypot.dbo."+symbol+" ORDER BY time DESC OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY") 
    cursor.execute(query)
    for item in cursor:
        return item[0]
    connection.commit()


#returns the transaction_id of the most recent transaction in the investments table
def get_transaction_number(buy_sell):
    global connection
    cursor = connection.cursor()
    query = ("SELECT TOP 1 transaction_id FROM crypot.dbo.investment_"+buy_sell+"_events ORDER BY transaction_id DESC") #get last transaction
    cursor.execute(query)
    current_num = 0
    for item in cursor:
        current_num = item[0]
    connection.commit()
    return current_num

#return total num_units for symbol in investment_sell_events table
def get_sum_sell_events(symbol):
    global connection
    cursor = connection.cursor()
    #this query needs to sum up number of units involved in buy events in table
    query = ("select units from crypot.dbo.investment_sell_events where symbol = ?;")
    cursor.execute(query, symbol)
    total = 0
    for item in cursor:
        total += item[0]
    connection.commit()
    return total

#return total num_units for symbol in investment_buy_events table
def get_sum_buy_events(symbol):
    global connection
    cursor = connection.cursor()
    #this query needs to sum up number of units involved in buy events in table
    query = ("select units from crypot.dbo.investment_buy_events where symbol = ?;")
    cursor.execute(query, symbol)
    total = 0
    for item in cursor:
        total += item[0]
    connection.commit()
    return total

def get_current_gain(symbol):
    current_coin_value = get_current_price_from_db(symbol)
    current_coin_owned = get_current_holdings(symbol)
    total_current_value = current_coin_owned * current_coin_value
    total_spent = get_cumulative_total(symbol)
    total_gain = total_current_value - total_spent
    return total_gain



#main()
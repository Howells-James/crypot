import plotly.graph_objects as go
import plotly.express as px
import datetime
import pyodbc
import socket
server = socket.gethostname()
server += "\\SQLEXPRESS"

connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')

##Price data

def get_x_data_string(coin):
    global connection
    cursor = connection.cursor()
    query = ("SELECT time FROM crypot.dbo."+coin+" ORDER BY time asc")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0].strip(' ')))
    connection.commit()
    return x

def get_y_data_string(coin):
    global connection
    cursor = connection.cursor()
    query = ("SELECT price FROM crypot.dbo."+coin+" ORDER BY time asc") 
    cursor.execute(query)
    y = []
    for item in cursor:
        y.append(str(item[0]).strip(' '))
    connection.commit()
    return y

##Buy data

def get_x_buy_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select time_aquired from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_units_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select units from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_y_buy_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select price_when_aquired from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    y = []
    for item in cursor:
        y.append(str(item[0]).strip(' '))
    connection.commit()
    return y

##Sell data

def get_x_sell_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select time_sold from crypot.dbo.investment_sell_events where symbol = '"+coin+"' order by time_sold asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_units_sold_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select units from crypot.dbo.investment_sell_events where symbol = '"+coin+"' order by time_sold asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_y_sell_data(coin):
    global connection
    cursor = connection.cursor()
    query = ("select price_when_sold from crypot.dbo.investment_sell_events where symbol = '"+coin+"' order by time_sold asc;")
    cursor.execute(query)
    y = []
    for item in cursor:
        y.append(str(item[0]).strip(' '))
    connection.commit()
    return y

##Helper Functions

def change_list_to_float(the_list):
    new_list = []
    for item in the_list:
        new_item = float(item)
        new_list.append(new_item)
    return new_list

def change_list_to_int(the_list):
    new_list = []
    for item in the_list:
        new_item = int(item)
        new_list.append(new_item)
    return new_list

#Graph Data Struct
class timeSlice():
    coinPrice = ''
    coinBuyPrice = ''
    timeStamp = ''
    amountSpent = 0
    coinSellPrice = ''
    sellTimeStamp = ''
    amountRecieved = 0
    def __init__(self, y, buyY, time, spend, sellTime, sellY, sell_amount):
        self.coinPrice = y
        self.coinBuyPrice = buyY
        if time is not None:
            newtime = str(time)[:19] #strips miliseconds and timezone
            self.timeStamp = datetime.datetime.strptime(newtime.strip(' \t\r\n'), '%Y-%m-%dT%H:%M:%S')
        if spend is not None:
            self.amountSpent = float(spend) * float(buyY) #calculate dollers spent
        else:
            self.amountSpent = 0
        self.coinSellPrice = sellY
        if sellTime is not None:
            newtime = str(sellTime)[:19] #strips miliseconds and timezone
            self.timeStamp = datetime.datetime.strptime(newtime.strip(' \t\r\n'), '%Y-%m-%dT%H:%M:%S')
        if sell_amount is not None:
            print(sell_amount + " " + sellY)
            self.amountRecieved = float(sell_amount) * float(sellY)
        else:
            self.amountRecieved = 0

    def to_string(self):
        ##print("self.coinPrice   :   self.coinBuyPrice  :  self.timeStamp :  self.amountSpent :  self.coinSellPrice :  self.sellTimeStamp :  self.amountRecieved")
        print(self.coinPrice , " : " , self.coinBuyPrice, " : " , self.timeStamp, " : " , self.amountSpent, " : " , self.coinSellPrice, " : ", self.sellTimeStamp, " : " , self.amountRecieved)


timeSliceList = []#list of moments in time
#create the list of moments in time
def createDataArray(coinAllTimeXData, coinAllTimePrice, buyXData, buyPrice, units_bought, sellXData, sellPrice, units_sold):
    merged_list1 = tuple(zip(coinAllTimeXData, coinAllTimePrice)) #Coin price vs time information
    for item in merged_list1:
        ts = timeSlice(item[1], None, item[0], None, None, None, None) #price, price when bought, time, amount bought, sell_price, sell time, amount recieved
        timeSliceList.append(ts)
    merged_list2 = tuple(zip(buyXData, buyPrice, units_bought)) #Coin bought price vs time + units sold
    for item in merged_list2:
        ts = timeSlice(item[1], item[1], item[0], item[2], None, None, None) #by definition we buy at the last recorded price so this works here. TODO will need to chage if this is ever buying real coin as the value will be different from the stored price of coin
        timeSliceList.append(ts)
    merged_list3 = tuple(zip(sellXData, sellPrice, units_sold)) #coin sold price vs time + units sold
    for item in merged_list3:
        ts = timeSlice(item[1], None, None, None, item[0], item[1], item[2])
        timeSliceList.append(ts)

def main(coin):
    x = get_x_data_string(coin) #time stamp from coin info table
    y = change_list_to_float(get_y_data_string(coin))  #price at time from coin info table
    xcoinbuydata = get_x_buy_data(coin) #time bought
    ycoinbuydata = get_y_buy_data(coin) #price when bought
    unitscoinbuydata = get_units_data(coin) #amount bought (not used... yet)
    xcoinselldata = get_x_sell_data(coin) #time sold
    ycoinselldata = get_y_sell_data(coin) #price when sold
    unitscoinselldata = get_units_sold_data(coin) #amount sold (not used... yet)
    

    
    createDataArray(x, y, xcoinbuydata, ycoinbuydata, unitscoinbuydata, xcoinselldata, ycoinselldata, unitscoinselldata)
    timeSliceList.sort(key=lambda x: x.timeStamp, reverse=False)
    for item in timeSliceList:
        item.to_string()
    fig = go.Figure()

    xlist = []
    ylist1 = []
    ylist2 = []
    ylist3 = []
    buySize = []
    for item in timeSliceList:
        xlist.append(item.timeStamp)
        ylist1.append(item.coinPrice)
        ylist2.append(item.coinBuyPrice)
        ylist3.append(item.coinSellPrice)
        buySize.append(item.amountSpent)
    fig.add_trace(go.Scatter(x=xlist, y=ylist1))
    fig.add_trace(go.Scatter(x=xlist, y=ylist2, mode='markers', marker_size=buySize))
    fig.add_trace(go.Scatter(x=xlist, y=ylist3, mode='markers', marker_size=10))
    fig.show()
    timeSliceList.clear()


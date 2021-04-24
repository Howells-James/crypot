import plotly.graph_objects as go
import plotly.express as px
import datetime
import pyodbc
import socket
server = socket.gethostname()
server += "\\SQLEXPRESS"


def get_x_data_string(coin):
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    query = ("SELECT time FROM crypot.dbo."+coin+" ORDER BY time asc")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0].strip(' ')))
    connection.commit()
    return x

def get_y_data_string(coin):
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    query = ("SELECT price FROM crypot.dbo."+coin+" ORDER BY time asc") 
    cursor.execute(query)
    y = []
    for item in cursor:
        y.append(str(item[0]).strip(' '))
    connection.commit()
    return y

def get_x_buy_data(coin):
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    query = ("select time_aquired from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_units_data(coin):
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    query = ("select units from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    x = []
    for item in cursor:
        x.append(str(item[0]).strip(' '))
    connection.commit()
    return x

def get_y_buy_data(coin):
    connection = pyodbc.connect('Driver={SQL Server};''Server='+server+';''Database=crypot;''Trusted_Connection=yes;')
    cursor = connection.cursor()
    query = ("select price_when_aquired from crypot.dbo.investment_buy_events where symbol = '"+coin+"' order by time_aquired asc;")
    cursor.execute(query)
    y = []
    for item in cursor:
        y.append(str(item[0]).strip(' '))
    connection.commit()
    return y

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

class timeSlice():
    coinPrice = ''
    coinBuyPrice = ''
    timeStamp = ''
    amountSpent = 0
    def __init__(self, y, buyY, time, spend):
        self.coinPrice = y
        self.coinBuyPrice = buyY
        newtime = str(time)[:19] #strips miliseconds and timezone
        self.timeStamp = datetime.datetime.strptime(newtime.strip(' \t\r\n'), '%Y-%m-%dT%H:%M:%S')
        if spend is not None:
            self.amountSpent = float(spend) * float(buyY) #calculate dollers spent
        else:
            self.amountSpent = 0

    def to_string(self):
        print(self.coinPrice , " : " , self.coinBuyPrice, " : " , self.timeStamp, " : " , self.amountSpent)


timeSliceList = []
def createDataArray(coinAllTimeXData, coinAllTimePrice, buyXData, buyPrice, units):
    merged_list1 = tuple(zip(coinAllTimeXData, coinAllTimePrice))
    for item in merged_list1:
        ts = timeSlice(item[1], None, item[0], None)
        timeSliceList.append(ts)
    mergerd_list2 = tuple(zip(buyXData, buyPrice, units))
    for item in mergerd_list2:
        ts = timeSlice(item[1], item[1], item[0], item[2]) #by definition we buy at the last recorded price so this works here. TODO will need to chage if this is ever buying real coin as the value will be different from the stored price of coin
        timeSliceList.append(ts)

def main(coin):
    x = get_x_data_string(coin)
    y = change_list_to_float(get_y_data_string(coin)) 
    xcoinbuydata = get_x_buy_data(coin)
    ycoinbuydata = get_y_buy_data(coin)
    unitscoinbuydata = get_units_data(coin)

    
    createDataArray(x, y, xcoinbuydata, ycoinbuydata, unitscoinbuydata)
    timeSliceList.sort(key=lambda x: x.timeStamp, reverse=False)
    fig = go.Figure()

    xlist = []
    ylist1 = []
    ylist2 = []
    buySize = []
    for item in timeSliceList:
        xlist.append(item.timeStamp)
        ylist1.append(item.coinPrice)
        ylist2.append(item.coinBuyPrice)
        buySize.append(item.amountSpent)
    fig.add_trace(go.Scatter(x=xlist, y=ylist1))
    fig.add_trace(go.Scatter(x=xlist, y=ylist2, mode='markers', marker_size=10))
    fig.show()
    timeSliceList.clear()

import plotly.graph_objects as go
import plotly.express as px
import pyodbc
import socket
server = socket.gethostname()
server += "\\SQLEXRPESS"


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
    print(x)
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
    print(y)
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

x = get_x_data_string('BTC')
y = change_list_to_float(get_y_data_string('BTC')) ##graph can only have one value array for x axis (time)

ethx = get_x_data_string('ETH')
ethy = change_list_to_float(get_y_data_string('ETH'))

xcoinbuydata = get_x_buy_data('BTC')
ycoinbuydata = get_y_buy_data('BTC')

fig = go.Figure(go.Scatter(x=x, y=y, line=dict(color="#FF0000")))
fig.add_trace(go.Scatter(x=x, y=ycoinbuydata, line=dict(color="#000000")))
#fig.add_trace(go.scatter(x=x, y=ycoinbuydata, line=dict(color="#FF0000")))
fig.show()
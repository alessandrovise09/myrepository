import pandas as pd
import yfinance as yf    
from finvizfinance.quote import finvizfinance
from pandas.io.html import read_html
import json
import requests

# Scarping Prezzi

def get_stock_data(symbol):
    
    data = yf.download(symbol, period="1d")
    return data

# Scarping Informazioni chiave
# la funzione 'ticker' di YFinance utile per accedere alle informazione del nostro asset

ticker = yf.Ticker('OLED')

print(ticker.info)
print(ticker.major_holders)
print(ticker.eps_trend)

asset = finvizfinance('oled')

print(ticker.recommendations)
print(ticker.analyst_price_targets)
print(ticker.funds_data)

apikey = '6xuiJYuWdJGPxaYfsb9GZuJSEOk43Mcy'

# Conto Economico
dataIS = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/OLED?apikey='+ apikey +'')
dataIS = dataIS.json()
IS = pd.DataFrame(dataIS).T
IS.columns = IS.iloc[0]
IS = IS.iloc[5:31,:10]

#BILANCIO
dataBS = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/OLED?apikey='+ apikey +'')
dataBS = dataBS.json()
BS = pd.DataFrame(dataBS).T
BS.columns = BS.iloc[0]
BS = BS.iloc[5:44,:10]

#FLUSSO DI CASSA
dataCF = requests.get(f'https://financialmodelingprep.com/api/v3/cash-flow-statement/OLED?apikey='+ apikey +'')
dataCF = dataCF.json()
CF = pd.DataFrame(dataCF).T
CF.columns = CF.iloc[0]
CF = CF.iloc[5:35,:10]

# Stampa i risultati

print(IS)
print(BS)
print(CF)

# performance.morningstar.com
#ispeziona elemento, console, network, XHR, trailing-total-returns

url = 'https://performance.morningstar.com/perform/Performance/stock/trailing-total-returns.action?&t=OLED&region=usa&culture=en-US&ops=clear&cur=&s=0P00001L8R|0P00001MLD|0P00001MK8|0P00001G3X|0P00001G7E'

#NASDAQ Benchmark  |0P00001MLD
#S&P500 Benchmark  |0P00001MK8
#MSCI World Benchmark  |0P00001L8R
#RUSSELL 1000 Benchmark  |0P00001G3X
#RUSSELL 2000 Benchmark  |0P00001G7E

tbl = read_html(url, attrs={'class':'r_table3  width955px print97'})

TRstock = pd.DataFrame(tbl[0])

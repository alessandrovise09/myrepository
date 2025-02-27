import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import numpy as np
import plotly.graph_objects as go

url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
tables = pd.read_html(url)

dow_jones_constituents = None
for i, table in enumerate(tables):
    if 'Symbol' in table.columns:
        dow_jones_constituents = table
        break

dow_jones_constituents['Symbol'] = dow_jones_constituents['Symbol'].str.replace('.', '-')
output_folder = r"C:\Users\aless\OneDrive\Desktop\PYTHON\FINANCE"
dow_jones_constituents.to_csv(os.path.join(output_folder, 'dow_jones_constituents.csv'), index=False)

start_date = datetime.now() - timedelta(days=365*10)
import time

tickers = dow_jones_constituents['Symbol'].tolist()
attempts = 5  

for attempt in range(attempts):
    try:
        stock_data = investing.download(tickers, start=start_date)['Adj Close']
        break  
    except Exception as e:
        print(f"Tentativo {attempt + 1} fallito. Errore: {e}")
        time.sleep(5)  

stock_data = stock_data.stack().reset_index()
stock_data.columns = ['Date', 'Symbol', 'Adj Close']
stock_data.to_csv(os.path.join(output_folder, 'dow_jones_data.csv'), index=False)

if stock_data.empty:
    print("Errore: i dati di mercato non sono stati scaricati correttamente.")
    exit()

file_path = r"C:\Users\aless\OneDrive\Desktop\PYTHON\FINANCE\dow_jones_constituents.csv"
dj_constituents = pd.read_csv(file_path)
file_path = r"C:\Users\aless\OneDrive\Desktop\PYTHON\FINANCE\dow_jones_data.csv"
dj_data = pd.read_csv(file_path)
dj_data = dj_data.ffill()

dj_data.sort_values(['Symbol', 'Date'], inplace=True)
dj_data['Daily Return'] = dj_data.groupby('Symbol')['Adj Close'].pct_change()

lowest_daily_returns = (
    dj_data[dj_data['Date'] != dj_data['Date'].min()]
    .groupby('Date', group_keys=False)
    .apply(lambda x: x.nsmallest(10, 'Daily Return'))
    .reset_index(drop=True)
)


lowest_daily_returns['Date'] = pd.to_datetime(lowest_daily_returns['Date'])
dj_data['Date'] = pd.to_datetime(dj_data['Date'])

initial_capital = 100000
results = pd.DataFrame(columns=['Date', 'Capital'])

lowest_daily_returns = lowest_daily_returns.sort_values('Date')
dj_data = dj_data.sort_values('Date')

unique_dates = lowest_daily_returns['Date'].unique()

for i, current_date in enumerate(unique_dates[:-1]):
    next_date = unique_dates[i + 1]
    current_day_losers = lowest_daily_returns[lowest_daily_returns['Date'] == current_date].nsmallest(10, 'Daily Return')
    
    if len(current_day_losers) < 10:
        continue
    
    amount_per_stock = initial_capital / 10
    total_value = 0
    
    for _, stock in current_day_losers.iterrows():
        symbol = stock['Symbol']
        buy_price = stock['Adj Close']
        sell_price = dj_data[(dj_data['Date'] == next_date) & (dj_data['Symbol'] == symbol)]['Adj Close'].values
        
        if len(sell_price) == 0 or np.isnan(buy_price) or np.isnan(sell_price[0]):
            continue
        
        shares = amount_per_stock / buy_price
        value = shares * sell_price[0]
        total_value += value
    
    initial_capital = total_value if total_value > 0 else initial_capital
    new_row = pd.DataFrame({'Date': [next_date], 'Capital': [initial_capital]})
    new_row = new_row.dropna(axis=1, how='all')
    results = pd.concat([results, new_row], ignore_index=True)

final_capital = results['Capital'].iloc[-1]
total_return = (final_capital - 100000) / 100000 * 100
print(f"Final Capital: ${final_capital:.2f}")
print(f"Total Return: {total_return:.2f}%")

trading_days = 252
results['Capital Return'] = results['Capital'].pct_change() 
annual_return = (1 + results['Capital Return'].mean())**trading_days - 1
annual_volatility = results['Capital Return'].std() * (trading_days**0.5)
sharpe_ratio = annual_return / annual_volatility

print(f"Annualized Return : {annual_return*100:.2f}% ")
print(f"Annualized Volatility : {annual_volatility*100:.2f}% ")
print(f"Sharpe Ratio : {sharpe_ratio:.2f} ")

dia_data = yf.download('DIA', start=start_date)
dia_data['Daily Return'] = dia_data['Adj Close'].pct_change()

annual_return_dia = (1 + dia_data['Daily Return'].mean())**trading_days - 1
annual_volatility_dia = dia_data['Daily Return'].std() * np.sqrt(trading_days)
sharpe_ratio_dia = annual_return_dia / annual_volatility_dia

print(f"Sharpe Ratio for DIA: {sharpe_ratio_dia:.2f} ")

if sharpe_ratio > sharpe_ratio_dia:
    print("Our mean reversion strategy outperformed the general Dow Jones.")
else:
    print("Our mean reversion strategy did not outperform the general Dow Jones.")

data = {
    'Mean Reversion Strategy': [annual_return, annual_volatility, sharpe_ratio],
    'DIA': [annual_return_dia, annual_volatility_dia, sharpe_ratio_dia]
}
df = pd.DataFrame(data, index=['Annual Return', 'Annual Std Dev', 'Sharpe Ratio'])
print(df)

higher_sharpe_ratio_strategy = df.idxmax(axis=1)['Sharpe Ratio']
print(f"\nStrategy with higher Sharpe Ratio: {higher_sharpe_ratio_strategy}")

results['Cumulative Return'] = (1 + results['Capital Return']).cumprod()
dia_data['Cumulative Return'] = (1 + dia_data['Daily Return']).cumprod()
results['Portfolio Value'] = results['Cumulative Return'] * 100000
dia_data['Portfolio Value'] = dia_data['Cumulative Return'] * 100000

fig = go.Figure()
fig.add_trace(go.Scatter(x=results['Date'], y=results['Portfolio Value'], mode='lines', name='Mean Reversion Strategy'))
fig.add_trace(go.Scatter(x=dia_data.index, y=dia_data['Portfolio Value'], mode='lines', name='DIA ETF'))
fig.update_layout(title='Growth of $100,000 Portfolio Over Time', xaxis_title='Date', yaxis_title='Portfolio Value ($)', legend_title='Strategy', autosize=False, width=1000, height=500)
print(fig.show())

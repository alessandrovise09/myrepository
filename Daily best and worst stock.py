import yfinance as yf
import pandas as pd
import datetime
import os

# Imposta la directory per i file salvati
output_folder =  r"C:\Users\aless\OneDrive\Desktop\PYTHON\FINANCE"


# Scarica la lista delle azioni globali (per semplicità useremo l'S&P 500)
sp500_tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]['Symbol'].tolist()

# Scarica dati giornalieri per le azioni
def get_stock_data(tickers):
    data = yf.download(tickers, period="1d", group_by='ticker')
    return data

# Identifica le migliori e peggiori azioni della giornata
def get_top_worst_performers(data):
    daily_returns = {}
    
    for ticker in sp500_tickers:
        try:
            open_price = data[ticker]['Open'].iloc[0]
            close_price = data[ticker]['Close'].iloc[0]
            daily_return = (close_price - open_price) / open_price
            daily_returns[ticker] = daily_return
        except:
            continue

    sorted_tickers = sorted(daily_returns, key=daily_returns.get)
    
    worst_10 = sorted_tickers[:10]  # Peggiori 10
    best_10 = sorted_tickers[-10:]  # Migliori 10

    return best_10, worst_10

# Calcola metriche finanziarie per una lista di azioni
def calculate_metrics(tickers):
    result = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="90d")

        # Prezzo medio ultimi 90 giorni
        avg_price_90d = hist['Close'].mean()

        # Deviazione standard per volatilità
        daily_returns = hist['Close'].pct_change().dropna()
        volatility = daily_returns.std()

        # Sharpe Ratio (approssimato con risk-free rate = 0)
        sharpe_ratio = daily_returns.mean() / volatility if volatility != 0 else None

        # Profit Margin (se disponibile)
        try:
            profit_margin = stock.info.get("profitMargins", None)
        except:
            profit_margin = None

        result.append({
            "Ticker": ticker,
            "AvgPrice90D": avg_price_90d,
            "Volatility": volatility,
            "SharpeRatio": sharpe_ratio,
            "ProfitMargin": profit_margin
        })

    return pd.DataFrame(result)

# Funzione principale per aggiornare il database giornalmente
def update_daily_data():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Scarica i dati di oggi
    stock_data = get_stock_data(sp500_tickers)
    
    # Trova le migliori e peggiori 10 azioni
    best_10, worst_10 = get_top_worst_performers(stock_data)

    # Calcola le metriche finanziarie
    best_metrics = calculate_metrics(best_10)
    worst_metrics = calculate_metrics(worst_10)

    # Salva i dati giornalmente
    filename = os.path.join(output_folder, f"stock_data_{today}.csv")
    all_data = pd.concat([best_metrics, worst_metrics])
    all_data.to_csv(filename, index=False)

    print(f"Dati salvati in {filename}")

# Esegui lo script giornalmente
update_daily_data()

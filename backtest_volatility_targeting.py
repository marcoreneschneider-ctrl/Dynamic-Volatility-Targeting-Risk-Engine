import numpy as np
import pandas as pd
import yfinance as yf

if __name__ == "__main__":
  # Usiamo SPY per le azioni e SHV (Short Treasury Bond ETF) come sostituto del cash/liquidità
  tickers = ["SPY", "SHV"]
  print(
      "--- DOWNLOADING DATA VOLATILITY TARGETING (2006-2026) ---"
  )
  data = yf.download(
      tickers, start="2006-01-01", end="2026-01-01", progress=False
  )["Close"]
  data = data.dropna()

  # Parametri del Volatility Targeting
  target_vol = 0.05  # Volatilità annua desiderata: 5% (bassissima!)
  vol_window = 20  # Finestra di calcolo della volatilità mobile

  # 1. Calcolo della volatilità annualizzata mobile di SPY
  spy_returns = data["SPY"].pct_change()
  rolling_vol = spy_returns.rolling(window=vol_window).std() * np.sqrt(252)

  # 2. Calcolo della quota da investire in SPY (Target Vol / Vol Corrente)
  # Usiamo .shift(1) per evitare il look-ahead bias (usiamo i dati di ieri per oggi)
  weight_spy = (target_vol / rolling_vol).shift(1)

  # Limitiamo il peso tra 0% e 100% (niente leva finanziaria eccessiva)
  weight_spy = weight_spy.clip(lower=0.0, upper=1.0)
  weight_spy = weight_spy.fillna(0.0)

  # Il resto del capitale viene investito in SHV (Cash / Treasury a brevissima scadenza)
  weight_shv = 1.0 - weight_spy

  # 3. Rendimenti giornalieri dei singoli asset
  shv_returns = data["SHV"].pct_change().fillna(0)

  # 4. Calcolo del rendimento giornaliero del portafoglio a Volatilità Target
  portfolio_returns = (weight_spy * spy_returns) + (weight_shv * shv_returns)
  portfolio_returns = portfolio_returns.dropna()

  # 5. Curva del capitale (partendo da 100.000 $)
  initial_capital = 100000
  equity_curve = initial_capital * (1 + portfolio_returns).cumprod()

  # 6. Analisi Anno per Anno
  annual_strategy = (
      equity_curve.resample("YE").last().pct_change() * 100
  )
  annual_spy = data["SPY"].resample("YE").last().pct_change() * 100

  df_years = pd.DataFrame({
      "Volatility Targeting 5% [%]": annual_strategy.round(2),
      "S&P 500 (Buy & Hold) [%]": annual_spy.round(2),
  })
  df_years = df_years.dropna()
  df_years.index = df_years.index.year

  print("\n" + "=" * 65)
  print(" ANNUAL PERFORMANCE: VOLATILITY TARGETING 5% VS S&P 500")
  print("=" * 65)
  print(df_years.to_string())
  print("=" * 65)

  # Metriche finali
  total_return = (equity_curve.iloc[-1] / initial_capital - 1) * 100
  ann_volatility = portfolio_returns.std() * np.sqrt(252) * 100
  neg_years = (df_years["Volatility Targeting 5% [%]"] < 0).sum()

  print(f"\nTotal return: {total_return:.2f}%")
  mean_returns = df_years["Volatility Targeting 5% [%]"].mean()
  print(f"Average yearly return: {mean_returns:.2f}%")
  print(f"Annualized volatily: {ann_volatility:.2f}%  <-- (Under 6%!)")
  print(
      f"Years closed with negative returns: {neg_years} su {len(df_years)}"
      " (Goal: max 2)"
  )

  df_years.to_csv("performance_vol_targeting_annual.csv")
  print("\nTable saved as: 'performance_vol_targeting_annual.csv'")


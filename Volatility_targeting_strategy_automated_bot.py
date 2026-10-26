import numpy as np
import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

# --- API AND PARAMETERS ---
ALPACA_API_KEY = "YOUR APY KEY"
ALPACA_SECRET_KEY = "YOUR SECRET APY KEY"

TARGET_VOL = 0.05  # Desired annual volatility: 5%
VOL_WINDOW = 20  # Mobile window of calculations


def calculate_target_weights():
  print("Step 1: Downloading recent data and calculating volatility...")

  # We download the last 60 days to have enough past data for the mobile average at 20 days
  data = yf.download(["SPY", "SHV"], period="60d", progress=False)["Close"]

  # Calculation of the mobile volatility at 20 days of SPY
  spy_returns = data["SPY"].pct_change()
  rolling_vol = spy_returns.rolling(window=VOL_WINDOW).std() * np.sqrt(252)

  # We use the second-last value (.iloc[-2]) which corresponds yesterdays closure
  # This avoids the look-ahead bias, exactlt like the backtest.
  current_vol = rolling_vol.iloc[-2]

  # Calculation of target weight for SPY
  weight_spy = TARGET_VOL / current_vol
  weight_spy = float(np.clip(weight_spy, 0.0, 1.0))  # Limitato tra 0% e 100%
  weight_shv = 1.0 - weight_spy  # Il resto va in SHV (Cash)

  print(f"-> Annualized volatility SPY (yesterday): {current_vol*100:.2f}%")
  print(f"-> Target weight calculated for SPY: {weight_spy*100:.2f}%")
  print(f"-> Target weight calculated for SHV: {weight_shv*100:.2f}%")

  return weight_spy, weight_shv


def rebalance_alpaca_portfolio(target_weight_spy, target_weight_shv):
  print("\nStep 2: Connecting to Alpaca Paper Trading...")
  trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

  account = trading_client.get_account()
  total_equity = float(account.equity)
  print(
      f"-> Succesfully connected! Total Portfolio value (Equity):"
      f" ${total_equity:,.2f}\n"
  )

  # Calculating countervalue in dollars desired for each asset
  target_val_spy = total_equity * target_weight_spy
  target_val_shv = total_equity * target_weight_shv

  print("Step 3: Controlling actual positions and executing orders...")

  # Obtaing our Alpaca's portfolio current positions
  positions = {
      p.symbol: float(p.market_value) for p in trading_client.get_all_positions()
  }
  current_spy_val = positions.get("SPY", 0.0)
  current_shv_val = positions.get("SHV", 0.0)

  # Calculating the difference between the desired value and the actual one
  diff_spy = target_val_spy - current_spy_val
  diff_shv = target_val_shv - current_shv_val

  # --- SPY ORDER ---
  # Using the "notional" orders (in dollars) because they are practical for the rebalancing
  if abs(diff_spy) > 5.0:  # Minimum treshold of $5 to avoid micro-transactions
    side = OrderSide.BUY if diff_spy > 0 else OrderSide.SELL
    notional_amount = round(abs(diff_spy), 2)
    try:
      order_data = MarketOrderRequest(
          symbol="SPY",
          notional=notional_amount,
          side=side,
          time_in_force=TimeInForce.DAY,
      )
      submitted = trading_client.submit_order(order_data)
      print(
          f"   [SUCCESS] SPY -> {side.name} di ${notional_amount:,.2f} | ID:"
          f" {submitted.id}"
      )
    except Exception as e:
      print(f"   [FAILED] Impossible to order SPY: {e}")
  else:
    print("   [SPY] Already balanced (no necessary action).")

  # --- SHV ORDER ---
  if abs(diff_shv) > 5.0:
    side = OrderSide.BUY if diff_shv > 0 else OrderSide.SELL
    notional_amount = round(abs(diff_shv), 2)
    try:
      order_data = MarketOrderRequest(
          symbol="SHV",
          notional=notional_amount,
          side=side,
          time_in_force=TimeInForce.DAY,
      )
      submitted = trading_client.submit_order(order_data)
      print(
          f"   [SUCCESS] SHV -> {side.name} di ${notional_amount:,.2f} | ID:"
          f" {submitted.id}"
      )
    except Exception as e:
      print(f"   [FAILED] Impossible to order SHV: {e}")
  else:
    print("   [SHV] Already balanced (no necessary action).")


if __name__ == "__main__":
  # 1. Calculates the target weights based on yesterday's volatility
  w_spy, w_shv = calculate_target_weights()

  # 2. Executes the rebalancing on Alpaca
  rebalance_alpaca_portfolio(w_spy, w_shv)
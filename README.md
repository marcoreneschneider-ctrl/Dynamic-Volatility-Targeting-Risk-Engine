# Dynamic-Volatility-Targeting-Risk-Engine
A quantitative Risk Engine in Python backtesting a Dynamic Volatility Targeting strategy (2008-2026). Designed to dynamically rebalance assets between SPY (S&P 500) and SHV (Short-Term US Treasuries) to maintain portfolio volatility below 6% and protect capital during major market crashes.

📊 Backtest Highlights (2008 – 2025)
- 2008 Financial Crash: Strategy lost only -5.24% vs. -36.80% for the S&P 500.
- 2022 Market Downturn: Strategy lost -4.35% vs. -18.18% for the S&P 500.
- **Annualized Volatility: Capped at 5.63% (Target Volatility set to 5%).
- Total Strategy Return: +158.94% across 18 years, with only 3 negative years.
- Methodology: Lagged position weights (`.shift(1)`) to eliminate look-ahead bias.

## 🛠️ Tech Stack
- Languages & Libraries: Python, NumPy, Pandas, yfinance.

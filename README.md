# Dynamic-Volatility-Targeting-Risk-Engine

For this project, I've put myself in the mind of a high-net-worth individual who is satisfied with lower returns (because they still make him lots of money) but wants to protect himself from market volatility.

So I tried to find an investment strategy with lower volatility than the S&P 500 that could be more attractive to someone with huge capital. The goals for the strategy were:

- An annual volatility under 6%, lower than the S&P 500's (which has historically been between 15-16%)
- Less than 3 out of the last 18 years (2008-2026) closed in a loss.
- To show significantly lower losses in major market crashes.

P.S. A volatility of 15% means that in 68% of the years, which equals a Standard Deviation, the price of the S&P 500 shifted by ±15%.

So I've started by backtesting various investment strategies with Python to find the best one. The previous ones I've tested
were based on technical indicators such as the RSI and EMA. Still, even after changing the parameters of these multiple times, the backtest results weren't satisfying.

After many attempts, I finally found a good strategy based on volatility targeting; here is how it works:

-It is set to maintain a steady 5% annual risk level.

-It calculates 20-day rolling annualized volatility for SPY using historical data while avoiding look-ahead bias.

-It dynamically adjusts asset weights: holding more SPY in calm markets and shifting into safe cash (SHV) when volatility spikes.

The results of the backtest of this strategy were:

- 5.63% annualized volatility, successfully reaching the <6% goal.

- +5.41% average annual return(pretty decent), and +158.94% 18-year total return (2008-2026).

- 3 out of 18 years closed with negative returns: so the <3 goal wasn't met, but looking at the backtest, it showed that in the 2008 Financial Crisis the strategy lost only -5.24% against the S&P 500's huge -36.80%! Also, during the market crash of 2022, the strategy only lost -4.38% compared to the S&P 500 loss of -18.18%.

Conclusion: I've managed to successfully find an investment strategy that works as a hedge against huge market crashes.
So after that, I've written another Python script that checks account equity and places orders on the Alpaca demo portfolio. I've created an automatic process that runs the script daily to evaluate target positions and submit orders right before the US stock market opens at 15:30 CET.

## Tech Stack & Tools

- **Language:** Python
- **Data Analysis & Quantitative Finance:** Pandas, NumPy
- **Broker & Execution API:** Alpaca Trade API (Paper Trading)
- **Data Source:** Yahoo Finance (`yfinance`) / Alpaca Market Data
- **Version Control:** Git, GitHub
- **Automation:** Cron / Scheduled Task Execution

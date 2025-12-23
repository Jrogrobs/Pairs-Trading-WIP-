# PFX Pairs Trading Dashboard (WIP)
A Python/Tkinter desktop dashboard for researching and monitoring FX pairs trading / statistical arbitrage setups. The app provides a simple GUI to select two FX pairs, choose frequency and strategy parameters, and run core spread/mean-reversion analytics.

**Key features:**
Interactive GUI (Tkinter/ttk): asset selection, data frequency, and strategy controls (entry/exit z-score, rolling window, stop-loss/take-profit, transaction costs).

Hedge ratio estimation methods:
OLS regression (static hedge ratio via statsmodels)
Kalman Filter (time-varying hedge ratio via pykalman)
Johansen cointegration (cointegration vector via coint_johansen)
Spread construction & monitoring: computes the spread based on the selected hedge-ratio method to support z-score signals and trade logic (to be expanded).
Plotting hooks (Matplotlib + TkAgg): placeholders for price overlays, spread + z-score charts, signal visualization, drawdowns, and live correlation panels.


**Status / TODO**
_Work in progress:_ execution logic, performance metrics, and trade logging are not fully implemented yet.
_Data integration:_ currently set up for a “Yahoo” placeholder; Interactive Brokers (IBKR) connection and live/streaming market data still need to be added.

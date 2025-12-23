# FX Pairs Trading Dashboard (WIP)

A lightweight Python + Tkinter desktop app for exploring FX pairs trading / statistical arbitrage ideas. Select two FX pairs, choose a hedge-ratio model, tune signal thresholds, and generate the spread used for mean-reversion signals — all from a simple GUI.

![Screenshot of the App]([https://github.com/Jrogrobs/Pairs-Trading-WIP-/blob/main/pairs_trading_app.png])

**What’s inside**

_GUI Dashboard (Tkinter/ttk)_   
* Asset selection + strategy controls (frequency, rolling window, entry/exit z-scores, stop-loss, take-profit, transaction costs).

_Hedge Ratio Engines_   
* OLS (statsmodels): static hedge ratio + intercept   
* Kalman Filter (pykalman): time-varying hedge ratio / intercept   
* Johansen Cointegration: cointegration vector–based hedge ratio   

_Spread Construction_   
* Builds the spread based on the selected hedge-ratio method (foundation for z-score signals + trading logic).   

_Plotting Hooks (Matplotlib / TkAgg)_   
* Scaffolding for: price overlays, spread time series, z-score bands + entry/exit signals, drawdowns, rolling correlation.

**Status**

🚧 Work in Progress — strategy execution, performance analytics, and trade logging are still being built.

_TODO_   
✅ Finalise signal generation + backtest loop

✅ Add performance metrics + trade log outputs

🔌 Integrate Interactive Brokers (IBKR) for live/streaming data + execution

📊 Complete the embedded plots (spread, z-score, drawdown, correlation)

**Tech Stack**   
Python · pandas · numpy · statsmodels · pykalman · matplotlib · tkinter

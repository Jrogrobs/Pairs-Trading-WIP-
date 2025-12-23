import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import statsmodels.api as sm
from pykalman import KalmanFilter
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
warnings.filterwarnings('ignore')

## TODO add Interactive brokers as data source

class PairsTradingDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("FX Pairs Trading Dashboard")
        self.root.geometry("1200x920")

        self._build_ui()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        for r in (2, 3, 4, 5):
            main.rowconfigure(r, weight=1)

        header = ttk.Label(main, text="FX Pairs Trading Strategy", font=("Calibri", 14, "bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 5))

        inputs = ttk.LabelFrame(main, text="Inputs", padding=10)
        inputs.grid(row=1, column=0, sticky="ew")
        for c in range(5):
            inputs.columnconfigure(c, weight=1)

        # --- Asset Selection ---
        ttk.Label(inputs, text="Asset Selection", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 2))
        ttk.Label(inputs, text="Trade type").grid(row=1, column=0, sticky="w")
        self.trade_type = tk.StringVar(value="FX")
        ttk.Combobox(inputs, textvariable=self.trade_type, values=["FX"], width=12, state="readonly").grid(row=1, column=1, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Data Source").grid(row=2, column=0, sticky="w")
        self.data_source = tk.StringVar(value="Yahoo")
        ttk.Combobox(inputs, textvariable=self.data_source, values=["Yahoo"], width=12, state="readonly").grid(row=2, column=1, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="FX Pair A").grid(row=3, column=0, sticky="w")
        self.asset_a = tk.StringVar(value="EURUSD")
        ttk.Combobox(inputs, textvariable=self.asset_a, values=["EURUSD"], width=12, state="readonly").grid(row=3, column=1, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="FX Pair B").grid(row=4, column=0, sticky="w")
        self.asset_b = tk.StringVar(value="GBPUSD")
        ttk.Combobox(inputs, textvariable=self.asset_b, values=["GBPUSD"], width=12, state="readonly").grid(row=4, column=1, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Data Frequency").grid(row=5, column=0, sticky="w")
        self.frequency = tk.StringVar(value="Daily")
        ttk.Combobox(inputs, textvariable=self.frequency, values=["Daily", "Weekly", "Monthly"], width=12, state="readonly").grid(row=5, column=1, sticky="w", padx=(0, 10))

        # Run button
        ttk.Button(inputs, text="Load & Analyse", command=self.run_pricing).grid(row=8, column=0, sticky="w", pady=(10, 0))

        # --- Strategy Control ---
        ttk.Label(inputs, text="Strategy Control", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, sticky="w", pady=(0, 2))
        ttk.Label(inputs, text="Hedge Ratio Method").grid(row=1, column=3, sticky="w")
        self.hedge_ratio = tk.StringVar(value="OLS")
        ttk.Combobox(inputs, textvariable=self.hedge_ratio, values=["OLS", "Kalman", "Johansen"], width=12, state="readonly").grid(row=1, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Z-Score Entry Thresholds").grid(row=2, column=3, sticky="w")
        self.entry_z = tk.StringVar(value="1.0")
        ttk.Entry(inputs, textvariable=self.entry_z, width=10).grid(row=2, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Exit Z-Score Threshold").grid(row=3, column=3, sticky="w")
        self.exit_z = tk.StringVar(value="0.5")
        ttk.Entry(inputs, textvariable=self.exit_z, width=10).grid(row=3, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Rolling Window (Days)").grid(row=4, column=3, sticky="w")
        self.rolling_window = tk.StringVar(value="30")
        ttk.Entry(inputs, textvariable=self.rolling_window, width=10).grid(row=4, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Stop Loss(%)").grid(row=5, column=3, sticky="w")
        self.stop_loss = tk.StringVar(value="0.1")
        ttk.Entry(inputs, textvariable=self.stop_loss, width=10).grid(row=5, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Take-Profit(%)").grid(row=6, column=3, sticky="w")
        self.take_profit = tk.StringVar(value="0.1")
        ttk.Entry(inputs, textvariable=self.take_profit, width=10).grid(row=6, column=4, sticky="w", padx=(0, 10))

        ttk.Label(inputs, text="Transaction Costs(%)").grid(row=7, column=3, sticky="w")
        self.transaction_costs = tk.StringVar(value="0.1")
        ttk.Entry(inputs, textvariable=self.transaction_costs, width=10).grid(row=7, column=4, sticky="w", padx=(0, 10))

        # --- Assumptions & Messages ---
        io = ttk.LabelFrame(main, text="Assumptions & Messages", padding=10)
        io.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        io.columnconfigure(0, weight=1)
        io.rowconfigure(0, weight=1)

        self.output_box = scrolledtext.ScrolledText(io, wrap=tk.WORD, height=6)
        self.output_box.grid(row=0, column=0, sticky="nsew")

        # --- Exposure Plot ---
        plot = ttk.LabelFrame(main, text="Exposure profiles (EE / ENE)", padding=10)
        plot.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        plot.columnconfigure(0, weight=1)
        plot.rowconfigure(0, weight=1)

        # --- Performance Metrics ---
        performance = ttk.LabelFrame(main, text="Performance", padding=10)
        performance.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        for c in range(6):
            performance.columnconfigure(c, weight=1)

        # --- Trade Log ---
        trade_log = ttk.LabelFrame(main, text="Trade Log", padding=10)
        trade_log.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        for c in range(6):
            trade_log.columnconfigure(c, weight=1)


    # --- Functions / Helpers ---
    @staticmethod
    def _parse_float(name, s):
        try:
            return float(str(s).strip())
        except Exception:
            raise ValueError(f"Invalid number for '{name}': {s}")
    
    @staticmethod
    def _pay_freq_to_int(freq_label: str) -> int:
        m = {"Annual": 1, "Semiannual": 2, "Quarterly": 4, "Monthly":12, "Daily":360}
        return m.get(freq_label, 2)    

    @staticmethod    
    def _hedge_ratio_ols(y, x):
        x = sm.add_constant(x)
        model = sm.OLS(y, x).fit()
        return model.params[1], model.params[0]

    @staticmethod
    def _hedge_ratio_kalman(y, x):
        delta = 1e-5
        trans_cov = delta / (1 - delta) * np.eye(2)
        obs_mat = np.expand_dims(np.vstack([x, np.ones(len(x))]).T, axis=1)

        kf = KalmanFilter(
            n_dim_obs=1,
            n_dim_state=2,
            initial_state_mean=[0, 0],
            initial_state_covariance=np.ones((2, 2)),
            transition_matrices=np.eye(2),
            observation_matrices=obs_mat,
            observation_covariance=1.0,
            transition_covariance=trans_cov
        )
        state_means, _ = kf.filter(y.values)
        hedge_ratios = state_means[:, 0]
        intercepts = state_means[:, 1]
        return hedge_ratios, intercepts

    @staticmethod
    def _hedge_ratio_johansen(df, det_order=0, k_ar_diff=1):
        result = coint_johansen(df, det_order, k_ar_diff)
        vec = result.evec[:, 0]
        hedge_ratio = vec[1] / vec[0]
        return hedge_ratio, 0

    @staticmethod
    def _calculate_spread(self, method, y, x):
        if method == 'OLS':
            beta, alpha = self._hedge_ratio_ols(y, x)
            spread = y - beta * x - alpha
        elif method == 'Kalman':
            hedge_ratios, intercepts = self._hedge_ratio_kalman(y, x)
            spread = y - hedge_ratios * x - intercepts
        elif method == 'Johansen':
            df = pd.concat([y, x], axis=1)
            beta, alpha = self._hedge_ratio_johansen(df)
            spread = y - beta * x
        else:
            raise ValueError("Unknown hedge ratio method")
        return spread
 

    # --- Run Analysis ---
    def run_pricing(self):
        try:
            # - Parse Inputs -
            trade_type = self.trade_type.get()
            data_source = self.data_source.get()
            asset_a = self.asset_a.get()
            asset_b = self.asset_b.get()
            data_freq = self._pay_freq_to_int(self.frequency.get())
            hedge_ratio = self._parse_float("Hedge Ratio Method", self.hedge_ratio.get())
            entry_z = self._parse_float("Z-Score Entry Thresholds", self.entry_z.get())
            entry_z = self._parse_float("Exit Z-Score Threshold", self.exit_z.get())
            rolling_window = self._parse_float("Rolling Window", self.rolling_window.get())
            stop_loss = self._parse_float("Stop Loss", self.stop_loss.get())
            take_profit = self._parse_float("Take Profit", self.take_profit.get())
            transaction_costs = self._parse_float("Transaction Costs", self.transaction_costs.get())



            # - Update Results -

            # - Assumtions / Summary Text -
            txt = []
            txt.append("✅ Pricing completed.\n")

            # - Plot Results -
            # price overlay A and B
            # time series spread
            # z score with entry and exit signals
            #drawdown
            # live correlation


        except Exception as e:
            messagebox.showerror("Input error", str(e))

def main():
    root = tk.Tk()
    app = PairsTradingDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()

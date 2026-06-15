import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_upi_data():
    # Date range: April 2016 (Launch) to June 2024
    dates = pd.date_range(start='2016-04-01', end='2024-06-01', freq='MS')
    n_months = len(dates)

    t = np.arange(n_months)
    upi_volume = []
    upi_value = []

    curr_vol = 0.03 # Lakhs in April 2016
    curr_val = 3.0 # Cr in April 2016

    for i, date in enumerate(dates):
        # Seasonality factor
        month = date.month
        seasonality = 1.0
        if month in [10, 11]: # Festive season
            seasonality = 1.15
        elif month == 12: # Year end
            seasonality = 1.10
        elif month == 3: # Year end financial
            seasonality = 1.05

        # Growth acceleration logic
        if date < datetime(2017, 1, 1):
            growth = 1.5
        elif date < datetime(2019, 1, 1):
            growth = 1.12
        elif date < datetime(2021, 1, 1):
            growth = 1.09
        else:
            growth = 1.05

        curr_vol *= (growth + np.random.normal(0, 0.01))
        curr_val *= (growth + np.random.normal(0, 0.01))

        upi_volume.append(curr_vol * seasonality)
        upi_value.append(curr_val * seasonality)

    df = pd.DataFrame({'Date': dates, 'UPI_Volume_Lakhs': upi_volume, 'UPI_Value_Cr': upi_value})

    # Scale to Real World 2024: ~14 Billion transactions = 1,40,000 Lakhs
    scale_factor_vol = 140000 / df['UPI_Volume_Lakhs'].iloc[-1]
    df['UPI_Volume_Lakhs'] *= scale_factor_vol

    # Scale to Real World 2024: ~20 Lakh Crore = 20,00,000 Crore
    scale_factor_val = 2000000 / df['UPI_Value_Cr'].iloc[-1]
    df['UPI_Value_Cr'] *= scale_factor_val

    # Other Payment Methods (Synthetic trends)
    df['IMPS_Volume_Lakhs'] = 500 * np.power(1.02, t) * (1 + 0.05 * np.sin(2 * np.pi * t / 12))
    df['IMPS_Value_Cr'] = 100000 * np.power(1.02, t)

    df['Cards_Volume_Lakhs'] = 5000 * np.power(1.005, t)
    df['Cards_Value_Cr'] = 150000 * np.power(1.008, t)

    df['ATM_Volume_Lakhs'] = 8000 * (1 - 0.001 * t)
    df['ATM_Value_Cr'] = 300000 * (1 + 0.001 * t)

    # Derived
    df['Average_Ticket_Size'] = (df['UPI_Value_Cr'] * 10**7) / (df['UPI_Volume_Lakhs'] * 10**5)

    return df

if __name__ == "__main__":
    df = generate_upi_data()
    df.to_csv('upi_data.csv', index=False)
    print("Corrected upi_data.csv generated successfully.")
    print(df.tail())

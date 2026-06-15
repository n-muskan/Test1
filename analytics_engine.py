import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
import datetime

class UPIAnalyticsEngine:
    def __init__(self, data_path='upi_data.csv'):
        self.df = pd.read_csv(data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.prepare_data()

    def prepare_data(self):
        self.df = self.df.sort_values('Date')

        # Calculated Measures
        self.df['MoM_Growth_Vol'] = self.df['UPI_Volume_Lakhs'].pct_change() * 100
        self.df['YoY_Growth_Vol'] = self.df['UPI_Volume_Lakhs'].pct_change(12) * 100
        self.df['MoM_Growth_Val'] = self.df['UPI_Value_Cr'].pct_change() * 100
        self.df['YoY_Growth_Val'] = self.df['UPI_Value_Cr'].pct_change(12) * 100

        self.df['Rolling_3M_Vol'] = self.df['UPI_Volume_Lakhs'].rolling(window=3).mean()
        self.df['Rolling_12M_Vol'] = self.df['UPI_Volume_Lakhs'].rolling(window=12).mean()
        self.df['Growth_Acceleration'] = self.df['MoM_Growth_Vol'].diff()
        self.df['Vol_Val_Ratio'] = self.df['UPI_Volume_Lakhs'] / self.df['UPI_Value_Cr']

        # Transaction Density Index (Volume per day)
        self.df['Transaction_Density'] = self.df['UPI_Volume_Lakhs'] / 30

        # Digital Penetration Score
        share = self.get_market_share()
        self.df['Digital_Penetration_Score'] = share['UPI_Volume_Lakhs_Share'] * (1 + self.df['YoY_Growth_Vol'].fillna(0) / 200)

    def get_cagr(self, column='UPI_Volume_Lakhs'):
        first_val = self.df[column].iloc[0]
        last_val = self.df[column].iloc[-1]
        n_years = len(self.df) / 12
        return (pow(last_val / first_val, 1/n_years) - 1) * 100

    def get_seasonality_stats(self):
        return seasonal_decompose(self.df.set_index('Date')['UPI_Volume_Lakhs'], model='multiplicative', period=12)

    def get_forecast(self, periods=24):
        pdf = self.df[['Date', 'UPI_Volume_Lakhs']].rename(columns={'Date': 'ds', 'UPI_Volume_Lakhs': 'y'})
        model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        model.fit(pdf)
        future = model.make_future_dataframe(periods=periods, freq='MS')
        return model.predict(future)

    def get_market_share(self):
        cols = ['UPI_Volume_Lakhs', 'IMPS_Volume_Lakhs', 'Cards_Volume_Lakhs', 'ATM_Volume_Lakhs']
        df_share = self.df[cols].copy()
        total = df_share.sum(axis=1)
        for col in cols:
            df_share[col + '_Share'] = (df_share[col] / total) * 100
        df_share['Date'] = self.df['Date']
        return df_share

    def generate_executive_insights(self):
        latest = self.df.iloc[-1]
        prev_year = self.df.iloc[-13] if len(self.df) > 13 else None
        insights = []

        yoy_vol = latest['YoY_Growth_Vol']
        insights.append({
            'impact': 'High',
            'title': 'Exponential Adoption',
            'text': f"UPI transaction volume grew {yoy_vol:.1f}% YoY, reaching {latest['UPI_Volume_Lakhs']/10000:.1f} Billion transactions this month."
        })

        ats_change = ((latest['Average_Ticket_Size'] / prev_year['Average_Ticket_Size']) - 1) * 100 if prev_year is not None else 0
        if ats_change < 0:
            insights.append({
                'impact': 'Medium',
                'title': 'Micro-payment Dominance',
                'text': f"Average ticket size declined by {abs(ats_change):.1f}% YoY, indicating deep penetration into small-ticket daily retail transactions."
            })

        if latest['Growth_Acceleration'] > 0:
            insights.append({
                'impact': 'Critical',
                'title': 'Growth Acceleration Warning',
                'text': "Growth is accelerating. Infrastructure should be audited for 2x capacity ahead of the festive season."
            })

        upi_share = self.get_market_share().iloc[-1]['UPI_Volume_Lakhs_Share']
        insights.append({
            'impact': 'High',
            'title': 'Market Dominance',
            'text': f"UPI now commands {upi_share:.1f}% of retail payment volumes, effectively displacing traditional debit cards."
        })

        return insights

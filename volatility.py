import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

def process_options_data(df, current_price, as_of_date=None):
    """
    Process options DataFrame with strike, expiry, and IV columns.
    
    Parameters:
        df (DataFrame): Input DataFrame with columns ['strike', 'expiry', 'iv']
        current_price (float): Current underlying asset price
        as_of_date (datetime): Reference date for time calculations (default: today)
    
    Returns:
        DataFrame: Processed DataFrame with new columns:
            - 'ttm' (time to expiry in years)
            - 'moneyness' (strike as % of current price)
            - 'iv' (interpolated implied volatility)
    """
    # Make copy to avoid modifying original DataFrame
    df = df.copy()
    
    # Set reference date
    as_of_date = as_of_date or datetime.now()
    
    # Convert expiry to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df['expiry']):
        df['expiry'] = pd.to_datetime(df['expiry'])
    
    # Calculate time to expiry in years
    df['ttm'] = (df['expiry'] - as_of_date).dt.days / 365.25
    
    # Calculate moneyness (strike as % of current price)
    df['moneyness'] = (df['strike'] / current_price) * 100
    
    # Sort by moneyness and ttm for proper interpolation
    df = df.sort_values(['moneyness', 'ttm'])
    
    # Interpolate missing IV values (linear interpolation)
    df['iv'] = df['iv'].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
    
    return df[['strike', 'expiry', 'ttm', 'moneyness', 'iv']]

# Example usage:
if __name__ == "__main__":
    # Sample data
    data = {
        'strike': [100, 105, 110, 95, 90, np.nan],
        'expiry': ['2023-12-15', '2023-12-15', '2024-01-19', '2023-12-15', '2024-01-19', '2024-01-19'],
        'iv': [0.25, 0.23, np.nan, 0.28, 0.30, np.nan]
    }
    df = pd.DataFrame(data)
    
    # Current price and date
    current_price = 102.50
    as_of_date = datetime(2023, 11, 1)
    
    # Process the data
    processed_df = process_options_data(df, current_price, as_of_date)
    print(processed_df)
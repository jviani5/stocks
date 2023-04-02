# import required libraries
import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd
from streamlit.hashing import _CodeHasher
import hashlib
import base64

# Define a function to generate a hash value for a given object


def hash_obj(obj):
    obj_str = str(obj).encode("utf-8")
    sha_hash = hashlib.sha256(obj_str).digest()
    return base64.urlsafe_b64encode(sha_hash).decode("utf-8")

# Define a SessionState class to persist variables across Streamlit runs


class SessionState:
    def __init__(self, **kwargs):
        self.hasher = _CodeHasher()
        self.kwargs = kwargs
        self.key = self.hash_args(kwargs)

    def __getattr__(self, name):
        return self.kwargs.get(name, None)

    def __setattr__(self, name, value):
        self.kwargs[name] = value

    def hash_args(self, args):
        h = self.hasher.hash(args)
        return hash_obj(h)


# ticker search feature in sidebar
st.sidebar.subheader("""Stock Search Web App""")
selected_stock = st.sidebar.text_input("Enter a valid stock ticker...", "GOOG")
button_clicked = st.sidebar.button("GO")

# Initialize the SessionState object
state = SessionState(df=pd.DataFrame(columns=["ticker", "price", "5yr %"]))


# main function
def main():
    global df
    st.subheader("""Daily **closing price** for """ + selected_stock)
    # get data on searched ticker
    stock_data = yf.Ticker(selected_stock)
    # get historical data for searched ticker
    stock_df = stock_data.history(period='1d', start='2020-01-01', end=None)
    # print line chart with daily closing prices for searched ticker
    st.line_chart(stock_df.Close)

    # Printing the latest price
    st.subheader("""Last **closing price** for """ + selected_stock)
    # get current date closing price for searched ticker
    last_price = stock_data.info['regularMarketPrice']
    # if market is closed on current date print that there is no data available
    st.write("The latest closing price is: ")
    st.write(last_price)

    # get daily volume for searched ticker
    st.subheader("""Daily **volume** for """ + selected_stock)
    st.line_chart(stock_df.Volume)

    # additional information feature in sidebar
    st.sidebar.subheader("""Display Additional Information""")

    # checkbox to display list of institutional shareholders for searched ticker
    major_shareholders = st.sidebar.checkbox("Institutional Shareholders")
    if major_shareholders:
        st.subheader("""**Institutional investors** for """ + selected_stock)
        display_shareholders = (stock_data.institutional_holders)
        if display_shareholders.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_shareholders)

    # checkbox to declare the stock is a daily gapper and to collect data
    gapper = st.sidebar.checkbox("Penny Stock Gapper")
    if gapper:
        st.subheader("""**Gap Information** for """ + selected_stock)
        isGapper = st.button(selected_stock + " is a gapper")
        if isGapper:
            # Get the current price of the selected stock using yfinance
            stock_info = yf.Ticker(selected_stock)
            current_price = stock_info.info['regularMarketPrice']

            # Get the price from 5 years ago
            five_yr_ago = (datetime.now() - pd.DateOffset(years=5)
                           ).strftime('%Y-%m-%d')
            hist = stock_info.history(start=five_yr_ago)

            # Calculate the percent change over the past 5 years
            pct_change = (current_price -
                          hist.iloc[0]['Close']) / hist.iloc[0]['Close'] * 100

            # Add a new row to the DataFrame with the selected stock ticker, price, and percent change over 5 years
            df = df.append({"ticker": selected_stock, "price": current_price,
                           "5yr %": pct_change}, ignore_index=True)

        empty_dataframe = st.button("Empty DataFrame")
        if empty_dataframe:
            # Reset the DataFrame to an empty state
            df = pd.DataFrame(columns=["ticker", "price", "5yr %"])

    # Print the updated DataFrame
    st.write(df)


if __name__ == "__main__":
    main()

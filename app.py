# import required libraries
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import requests

# ticker search feature in sidebar
st.sidebar.subheader("""Stock Search Web App""")
#home = st.sidebar.subheader("""Home""")
#if home:
#    url = 'https://www.barchart.com/stocks/pre-market-trading/percent-change/advances?orderBy=preMarketPercentChange&orderDir=desc'
#    response = requests.get(url)
#    df_list = pd.read_html(response.text)
#    df = df_list[0]  # select the first table in the list
#    st.write(df)
st.sidebar.subheader("""""")
selected_stock = st.sidebar.text_input("Why", "AAPL")

# Initialize an empty DataFrame with columns "ticker", "price", and "5yr %"
df = pd.DataFrame(columns=["ticker", "price", "5yr %"])

# main function
def main():
    global df
    # get data on searched ticker
    stock_data = yf.Ticker(selected_stock)
    last_price = stock_data.info['regularMarketPrice']

    # checkbox to display list of institutional shareholders for searched ticker
    long_term = st.sidebar.checkbox("...is a good buy")
    if long_term:
        st.subheader("""Daily **closing price** for """ + selected_stock)
        # calculate the date two years ago from today
        five_years_ago = (datetime.now() - timedelta(days=5*365)
                        ).strftime('%Y-%m-%d')
        # get historical data for searched ticker starting two years ago from today
        stock_df = stock_data.history(period='1d', start=five_years_ago, end=None)
        # print line chart with daily closing prices for searched ticker
        st.line_chart(stock_df.Close)

        # Printing the latest price
        st.subheader("""Last **closing price** for """ + selected_stock)
        # if market is closed on current date print that there is no data available
        st.write("The latest closing price is: ")
        st.write(last_price)

        # get daily volume for searched ticker
        st.subheader("""Daily **volume** for """ + selected_stock)
        st.line_chart(stock_df.Volume)
        st.subheader("""**Institutional investors** for """ + selected_stock)
        display_shareholders = (stock_data.institutional_holders)
        if display_shareholders.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_shareholders)

    # checkbox to declare the stock is a daily gapper and to collect data
    gapper = st.sidebar.checkbox("...is a gapper")
    if gapper:
        # create a candlestick chart of the selected stock for the past 1 day with 1 minute intervals
        st.subheader(f"""**Candlestick Chart** for {selected_stock}""")
        stock_data_df = stock_data.history(period='1d', interval='1m')
        fig = go.Figure(data=[go.Candlestick(x=stock_data_df.index,
                                             open=stock_data_df['Open'],
                                             high=stock_data_df['High'],
                                             low=stock_data_df['Low'],
                                             close=stock_data_df['Close'])])
        st.plotly_chart(fig)
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

            # Print the updated DataFrame
            st.write(df)

        empty_dataframe = st.button("Empty DataFrame")
        if empty_dataframe:
            # Reset the DataFrame to an empty state
            df = pd.DataFrame(columns=["ticker", "price", "5yr %"])

            with open("gappers.txt", "w") as f:
                f.write(df.to_string(index=False))

    good_trade = st.sidebar.checkbox("...is a good trade")
    if good_trade:
        # create a candlestick chart of the selected stock for the past 10 days with 15 minute intervals
        st.subheader(f"""**Candlestick Chart** for {selected_stock}""")
        stock_data_df = stock_data.history(period='10d', interval='15m')
        fig = go.Figure(data=[go.Candlestick(x=stock_data_df.index,
                                             open=stock_data_df['Open'],
                                             high=stock_data_df['High'],
                                             low=stock_data_df['Low'],
                                             close=stock_data_df['Close'])])
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()

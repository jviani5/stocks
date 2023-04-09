# import required libraries
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# ticker search feature in sidebar
st.sidebar.subheader("""Stock Search Web App""")
st.sidebar.subheader("""""")
home = st.sidebar.button("Home")
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
    five_years_ago = (datetime.now() - timedelta(days=5*365)
                        ).strftime('%Y-%m-%d')

    
    st.subheader("""Stocks That Gapped Up This Morning""")
    #get data of gappers from tradingview
    url = "https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/"
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")
    table = doc.find("table")
    trs = table.find_all("tr")
    rows = []
    def rowgetDataText(tr, coltag='td'): # td (data) or th (header)       
            return [td.get_text(strip=True) for td in tr.find_all(coltag)]
    headerow = rowgetDataText(trs[0], 'th')
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append(rowgetDataText(tr, 'td') ) # data row     
    #create dataframe to print on streamlit  
    dftable = pd.DataFrame(rows[1:], columns=rows[0])
    dftable.head(4)
    st.dataframe(dftable)
    #analysis on gapper
    st.subheader("Analysis")
    with st.form(key='my_form'):
        text_input = st.text_input(label='Enter Ticker')
        submit_button = st.form_submit_button(label='Submit')
    gapTickYF = yf.Ticker(text_input)
    #2 day chart
    st.subheader ("2 day, 1 minute chart")
    gapTickData = gapTickYF.history(period='2d', interval='1m')
    fig1 = go.Figure(data=[go.Candlestick(x=gapTickData.index,
                                            open=gapTickData['Open'],
                                            high=gapTickData['High'],
                                            low=gapTickData['Low'],
                                            close=gapTickData['Close'])])
    st.plotly_chart(fig1)
    #5 year daily chart
    st.subheader("5 year, 1 day chart")
    gapTickLongTerm = gapTickYF.history(period='1d', start=five_years_ago, end=None)
    st.line_chart(gapTickLongTerm.Close)



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

        empty_dataframe = st.button("Export to Sheets")
        if empty_dataframe:
            # Reset the DataFrame to an empty state
            df = pd.DataFrame(columns=["ticker", "price", "5yr %"])

            with open("gappers.txt", "w") as f:
                f.write(df.to_string(index=False))

    #checkbox to say the ticker is a good options swing trade
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

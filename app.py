# import required libraries
import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd


# ticker search feature in sidebar
st.sidebar.subheader("""Stock Search Web App""")
selected_stock = st.sidebar.text_input("Enter a valid stock ticker...", "GOOG")
button_clicked = st.sidebar.button("GO")
if button_clicked == "GO":
    main()

# main function


def main():
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

    # Initialize an empty DataFrame with columns "ticker" and "price"
    df = pd.DataFrame(columns=["ticker", "price"])

    # Get the selected stock ticker from user input
    selected_stock = st.text_input("Enter the stock ticker")

    # checkbox to declare the stock is a daily gapper and to collect data
    gapper = st.sidebar.checkbox("Penny Stock Gapper")
    if gapper:
        st.subheader("""**Gap Information** for """ + selected_stock)
        isGapper = st.button(selected_stock + " is a gapper")
        if isGapper:
            # Get the current price of the selected stock using yfinance
            stock_info = yf.Ticker(selected_stock)
            current_price = stock_info.info['regularMarketPrice']

            # Add a new row to the DataFrame with the selected stock ticker and price
            df = df.append({"ticker": selected_stock, "price": current_price}, ignore_index=True)

            # Print the updated DataFrame
            st.write(df)

        empty_dataframe = st.button("Empty DataFrame")
        if empty_dataframe:
            # Reset the DataFrame to an empty state
            df = pd.DataFrame(columns=["ticker", "price"])

            # Print a message to confirm that the DataFrame has been cleared
            st.write("DataFrame has been cleared")



if __name__ == "__main__":
    main()

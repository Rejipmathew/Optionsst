import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Option Chain Explorer")

# --- Sidebar for user input ---
with st.sidebar:
    ticker_symbol = st.text_input("Enter ticker symbol:", "TSLA")

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Get available expiration dates
        available_expirations = ticker.options
    except Exception as e:
        st.error(f"Error fetching ticker data: {e}")
        st.stop()

    # Expiration date input with available dates
    expiry_date = st.selectbox("Select expiry date:", available_expirations)

    # Fetch option chain data to get contract symbols
    try:
        option_chain = ticker.option_chain(expiry_date)
    except Exception as e:
        st.error(f"Error fetching option chain data: {e}")
        st.stop()

    # Combine calls and puts contract symbols and sort by volume
    all_contract_symbols = list(option_chain.calls['contractSymbol']) + \
                           list(option_chain.puts['contractSymbol'])
    all_contracts = pd.concat([option_chain.calls, option_chain.puts])
    all_contracts_sorted = all_contracts.sort_values(by='volume', ascending=False)
    all_contract_symbols_sorted = all_contracts_sorted['contractSymbol'].tolist()

    # Choose plotting parameter for the first plot
    plot_param = st.selectbox("Select parameter to plot (Chain):", ['lastPrice', 'volume', 'openInterest'])

    # Select option for the second plot using contractSymbol (default highest volume)
    default_option = all_contract_symbols_sorted[0]  # Highest volume contract
    selected_option = st.selectbox("Select option for price plot:", all_contract_symbols_sorted, index=all_contract_symbols_sorted.index(default_option))

# --- Create pages ---
page = st.sidebar.radio("Select Page", ["Option Chain", "Option Price", "Calls Table", "Puts Table"])

# --- Page 1: Option Chain Visualization ---
if page == "Option Chain":
    # --- Get current stock price ---
    try:
        current_price = ticker.info['currentPrice']
    except Exception as e:
        st.error(f"Error fetching stock price: {e}")
        st.stop()

    st.write(f"Current Price of {ticker_symbol}: {current_price}")

    st.subheader("Option Chain Visualization")

    # Combine calls and puts for plotting
    calls = option_chain.calls[['strike', 'lastPrice', 'volume', 'openInterest']]
    calls['type'] = 'Call'
    puts = option_chain.puts[['strike', 'lastPrice', 'volume', 'openInterest']]
    puts['type'] = 'Put'
    df = pd.concat([calls, puts])

    # Create the plot
    fig, ax = plt.subplots()
    for option_type in df['type'].unique():
        df_type = df[df['type'] == option_type]
        ax.plot(df_type['strike'], df_type[plot_param], label=option_type)

    ax.set_xlabel("Strike Price")
    ax.set_ylabel(plot_param)
    ax.set_title(f"{ticker_symbol} Option Chain ({expiry_date}) - {plot_param}")
    ax.legend()

    st.pyplot(fig)

# --- Page 2: Option Price History ---
elif page == "Option Price":
    st.subheader("Option Price History")

    try:
        # Fetch historical data for the selected option
        option_data = yf.download(selected_option, period="1mo")  # Download 1 month of data

        # Create the plot
        fig, ax = plt.subplots()
        ax.plot(option_data['Open'], label="Last Price")
        ax.plot(option_data['Low'], label="Bid")
        ax.plot(option_data['High'], label="Ask")

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title(f"{selected_option} Price History")
        ax.legend()

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error fetching or plotting option price data: {e}")

# --- Page 3: Calls Table ---
elif page == "Calls Table":
    st.subheader("Calls (Sorted by Volume)")
    st.write(option_chain.calls.sort_values(by='volume', ascending=False))

# --- Page 4: Puts Table ---
elif page == "Puts Table":
    st.subheader("Puts (Sorted by Volume)")
    st.write(option_chain.puts.sort_values(by='volume', ascending=False))

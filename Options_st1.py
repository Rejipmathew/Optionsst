import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Option Chain Explorer")

# --- Sidebar for user input ---
with st.sidebar:
    ticker_symbol = st.text_input("Enter ticker symbol:", "AAPL")

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Get available expiration dates
        available_expirations = ticker.options
    except Exception as e:
        st.error(f"Error fetching ticker data: {e}")
        st.stop()

    # Expiration date input with available dates
    expiry_date = st.selectbox("Select expiry date:", available_expirations)

    # Choose plotting parameter for the first plot
    plot_param = st.selectbox("Select parameter to plot (Chain):", ['lastPrice', 'volume', 'openInterest'])

    # Select option for the second plot
    selected_option = st.selectbox("Select option for price plot:", available_expirations)

# --- Main content area ---

# Fetch option chain data
try:
    option_chain = ticker.option_chain(expiry_date)
except Exception as e:
    st.error(f"Error fetching option chain data: {e}")
    st.stop()

# --- Get current stock price ---
try:
    current_price = ticker.info['currentPrice']
except Exception as e:
    st.error(f"Error fetching stock price: {e}")
    st.stop()

st.write(f"Current Price of {ticker_symbol}: {current_price}")

# --- Plotting Option Chain ---
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

st.pyplot(fig)  # Display plot above the tables


# --- Plotting Option Price ---
st.subheader("Option Price History")

try:
    # Fetch historical data for the selected option
    option_data = yf.download(selected_option, period="1mo")  # Download 1 month of data

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(option_data['Open'], label="Open")
    ax.plot(option_data['High'], label="High")
    ax.plot(option_data['Close'], label="Close")

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(f"{selected_option} Price History")
    ax.legend()

    st.pyplot(fig)

except Exception as e:
    st.error(f"Error fetching or plotting option price data: {e}")


# --- Display Calls and Puts (sorted by descending volume) ---
st.subheader("Calls (Sorted by Volume)")
st.write(option_chain.calls.sort_values(by='volume', ascending=False))

st.subheader("Puts (Sorted by Volume)")
st.write(option_chain.puts.sort_values(by='volume', ascending=False))

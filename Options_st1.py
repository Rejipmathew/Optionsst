import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Set up the page layout
st.set_page_config(page_title="Stock Option Analysis", layout="wide")

# Sidebar for user inputs
st.sidebar.title("Options Analysis Settings")
ticker = st.sidebar.text_input("Enter stock ticker (e.g., TSLA):", value="TSLA")
include_expired = st.sidebar.checkbox("Include expired options", value=False)
selected_date = None

# Add time period selection for historical data
st.sidebar.subheader("Select Historical Data Period")
data_period = st.sidebar.selectbox("Time Range:", ["1mo", "6mo", "1y", "5y"], index=0)

# Title
st.title("Stock Option Analysis")
st.markdown("Analyze stock options, visualize trends, and track specific option performance.")

if ticker:
    # Fetch stock data
    stock = yf.Ticker(ticker)
    option_dates = stock.options

    if option_dates:
        st.sidebar.subheader("Available Option Expiration Dates")
        selected_date = st.sidebar.selectbox("Choose an expiration date:", option_dates)
        if include_expired:
            st.sidebar.warning("Expired options will be fetched, which might take longer.")
    else:
        st.error("No option data available for this stock.")

    if selected_date:
        st.subheader(f"Options Data for {ticker} - Expiration Date: {selected_date}")
        # Fetch option chain for the selected date
        try:
            option_chain = stock.option_chain(selected_date)
            calls = option_chain.calls
            puts = option_chain.puts

            # Combine calls and puts for specific option analysis
            all_options = pd.concat([calls, puts]).reset_index(drop=True)
            st.sidebar.subheader("Analyze Specific Option")
            option_symbol = st.sidebar.selectbox("Select an option contract:", all_options["contractSymbol"].unique())

            # Display plots for the selected option
            if option_symbol:
                st.subheader(f"Trend Analysis for {option_symbol}")

                # Fetch historical data for the selected option
                try:
                    historical_data = yf.download(option_symbol, period=data_period, interval="1d")

                    # Validate and process data
                    if not historical_data.empty:
                        historical_data = historical_data.reset_index()

                        # **Fix:** Flatten multi-dimensional columns 
                        for col in historical_data.columns:
                            if historical_data[col].ndim > 1:
                                historical_data[col] = historical_data[col].apply(lambda x: x[0] if isinstance(x, (list, np.ndarray)) else x)

                        # Plot price trend
                        st.markdown("#### Price Trend")
                        price_fig = px.line(
                            historical_data,
                            x="Date",
                            y=["Open", "Close", "High", "Low"],
                            title=f"Price Trend for {option_symbol}",
                            labels={"value": "Price", "variable": "Metric", "Date": "Date"},
                        )
                        st.plotly_chart(price_fig, use_container_width=True)

                        # Plot volume trend
                        st.markdown("#### Volume Trend")
                        volume_fig = px.bar(
                            historical_data,
                            x="Date",
                            y="Volume",
                            title=f"Volume Trend for {option_symbol}",
                            labels={"Volume": "Volume", "Date": "Date"},
                        )
                        st.plotly_chart(volume_fig, use_container_width=True)

                        # Combined price and volume overlay plot
                        st.markdown("#### Combined Price and Volume Trend")
                        overlay_fig = go.Figure()

                        # Add price trends
                        overlay_fig.add_trace(go.Scatter(
                            x=historical_data["Date"],
                            y=historical_data["Close"],
                            mode="lines",
                            name="Close Price",
                            line=dict(color="blue", width=2),
                        ))

                        # Add volume bars
                        overlay_fig.add_trace(go.Bar(
                            x=historical_data["Date"],
                            y=historical_data["Volume"],
                            name="Volume",
                            marker=dict(color="rgba(255, 182, 193, 0.6)"),
                            yaxis="y2",
                        ))

                        # Configure layout for dual y-axes
                        overlay_fig.update_layout(
                            title=f"Price and Volume Trend for {option_symbol}",
                            xaxis_title="Date",
                            yaxis=dict(title="Price", titlefont=dict(color="blue"), tickfont=dict(color="blue")),
                            yaxis2=dict(
                                title="Volume",
                                titlefont=dict(color="red"),
                                tickfont=dict(color="red"),
                                anchor="x",
                                overlaying="y",
                                side="right",
                            ),
                            legend=dict(x=0.1, y=1.1, orientation="h"),
                            margin=dict(l=40, r=40, t=50, b=40),
                        )
                        st.plotly_chart(overlay_fig, use_container_width=True)
                    else:
                        st.error("No historical data available for this option.")
                except Exception as e:
                    st.error(f"Error fetching historical data: {e}")

            # Show sorted data by volume
            st.markdown("### Calls Data Sorted by Volume")
            calls_sorted = calls.sort_values(by="volume", ascending=False)
            st.dataframe(calls_sorted)

            st.markdown("### Puts Data Sorted by Volume")
            puts_sorted = puts.sort_values(by="volume", ascending=False)
            st.dataframe(puts_sorted)
        except Exception as e:
            st.error(f"Error fetching option chain data: {e}")

# Footer
st.markdown("---")
st.markdown("Created using [Streamlit](https://streamlit.io/) and [Yahoo Finance API](https://pypi.org/project/yfinance/).")
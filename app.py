import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Advanced Financial Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.positive {
    color: #00C851;
    font-weight: bold;
}
.negative {
    color: #FF4444;
    font-weight: bold;
}
.neutral {
    color: #666;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("📊 Financial Dashboard")

# Stock symbol input
st.sidebar.subheader("Stock Selection")
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol", 
    "PETR4.SA",
    help="Enter any stock symbol. See sectors below.",
    key="stock_input"
)

# Manual refresh button
if st.sidebar.button("🔄 Load Stock Data", type="primary"):
    st.session_state.force_refresh = True
    st.rerun()

# Sector-based stock selection (based on your Excel)
st.sidebar.subheader("📈 Sectors")

# Banking sector
with st.sidebar.expander("🏦 Bancos (Banks)"):
    bank_stocks = ["ITUB4.SA", "BBDC4.SA", "SANB11.SA", "BBAS3.SA"]
    for stock in bank_stocks:
        if st.button(f"{stock}", key=f"bank_{stock}"):
            st.session_state.selected_stock = stock
            st.session_state.force_refresh = True

# Oil & Energy sector
with st.sidebar.expander("⛽ Petróleo (Oil & Energy)"):
    oil_stocks = ["PETR4.SA", "PETR3.SA", "PRIO3.SA"]
    for stock in oil_stocks:
        if st.button(f"{stock}", key=f"oil_{stock}"):
            st.session_state.selected_stock = stock
            st.session_state.force_refresh = True

# Mining sector
with st.sidebar.expander("⛏️ Mineração (Mining)"):
    mining_stocks = ["VALE3.SA", "CSNA3.SA"]
    for stock in mining_stocks:
        if st.button(f"{stock}", key=f"mining_{stock}"):
            st.session_state.selected_stock = stock
            st.session_state.force_refresh = True

# Technology sector
with st.sidebar.expander("💻 Tecnologia (Technology)"):
    tech_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    for stock in tech_stocks:
        if st.button(f"{stock}", key=f"tech_{stock}"):
            st.session_state.selected_stock = stock
            st.session_state.force_refresh = True

# Use selected stock from buttons or detect input changes
if 'selected_stock' in st.session_state:
    stock_symbol = st.session_state.selected_stock
    # Clear the selected stock after using it
    del st.session_state.selected_stock

# Check if stock symbol has changed
if 'previous_stock' not in st.session_state:
    st.session_state.previous_stock = stock_symbol

stock_changed = st.session_state.previous_stock != stock_symbol
if stock_changed:
    st.session_state.previous_stock = stock_symbol
    st.session_state.force_refresh = True

# Timeframe selection
st.sidebar.subheader("📅 Time Period")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["Current", "5d", "30d", "YTD", "LTM", "Range"],
    index=0
)

update_interval = st.sidebar.slider("Update Interval (seconds)", 5, 60, 10)

# Main page header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("📊 Advanced Financial Dashboard")
    st.markdown("<p style='text-align: center; color: #666;'>Comprehensive Stock Analysis & Real-Time Data</p>", unsafe_allow_html=True)
st.markdown("---")

# Enhanced stock data function
def get_comprehensive_stock_data(symbol, timeframe="Current"):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Check if we got valid data
        if not info or info.get('regularMarketPrice') is None:
            st.error(f"❌ Could not find data for '{symbol}'. Please check:")
            st.error("• For US stocks: Use symbol only (e.g., AAPL, GOOGL)")
            st.error("• For Brazilian stocks: Add .SA suffix (e.g., PETR4.SA, VALE3.SA)")
            return None
        
        # Get historical data based on timeframe
        period_map = {
            "Current": "1d",
            "5d": "5d",
            "30d": "1mo",
            "YTD": "ytd",
            "LTM": "1y",
            "Range": "max"
        }
        
        hist = stock.history(period=period_map.get(timeframe, "1d"))
        
        # Calculate performance metrics
        current_price = info.get('regularMarketPrice', 0) or 0
        
        performance = {}
        if not hist.empty and current_price > 0:
            try:
                if timeframe == "5d" and len(hist) >= 5:
                    start_price = hist['Close'].iloc[-6] if len(hist) > 5 else hist['Close'].iloc[0]
                    if start_price > 0:
                        performance['5d'] = ((current_price - start_price) / start_price * 100)
                elif timeframe == "30d" and len(hist) >= 1:
                    start_price = hist['Close'].iloc[0]
                    if start_price > 0:
                        performance['30d'] = ((current_price - start_price) / start_price * 100)
                elif timeframe == "YTD" and len(hist) >= 1:
                    start_price = hist['Close'].iloc[0]
                    if start_price > 0:
                        performance['ytd'] = ((current_price - start_price) / start_price * 100)
                elif timeframe == "LTM" and len(hist) >= 1:
                    start_price = hist['Close'].iloc[0]
                    if start_price > 0:
                        performance['ltm'] = ((current_price - start_price) / start_price * 100)
            except (IndexError, ZeroDivisionError):
                pass  # Skip performance calculation if data is insufficient
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol) or symbol,
            'price': current_price or 0,
            'change': info.get('regularMarketChange', 0) or 0,
            'change_percent': info.get('regularMarketChangePercent', 0) or 0,
            'volume': info.get('regularMarketVolume', 0) or 0,
            'previous_close': info.get('regularMarketPreviousClose', 0) or 0,
            'market_cap': info.get('marketCap', 0) or 0,
            'pe_ratio': info.get('trailingPE', 0) or 0,
            'dividend_yield': info.get('dividendYield', 0) or 0,
            'beta': info.get('beta', 0) or 0,
            '52_week_high': info.get('fiftyTwoWeekHigh', 0) or 0,
            '52_week_low': info.get('fiftyTwoWeekLow', 0) or 0,
            'performance': performance,
            'hist': hist if not hist.empty else pd.DataFrame()
        }
    except Exception as e:
        st.error(f"❌ Error fetching data for '{symbol}': {str(e)}")
        return None

# Enhanced display function
def display_comprehensive_dashboard(data, timeframe):
    if not data:
        return
    
    # Header with stock name and current price
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"{data['name']} ({data['symbol']})")
    with col2:
        price = data.get('price', 0) or 0
        st.markdown(f"<h2 style='color: {'#00C851' if (data.get('change', 0) or 0) >= 0 else '#FF4444'};'>${price:.2f}</h2>", unsafe_allow_html=True)
    with col3:
        change = data.get('change', 0) or 0
        change_percent = data.get('change_percent', 0) or 0
        change_color = "positive" if change >= 0 else "negative"
        st.markdown(f"<h3 class='{change_color}'>{change:+.2f} ({change_percent:+.2f}%)</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Timeframe buttons
    st.subheader("📅 Timeframe Selection")
    timeframe_cols = st.columns(6)
    timeframes = ["Current", "5d", "30d", "YTD", "LTM", "Range"]
    
    for i, tf in enumerate(timeframes):
        with timeframe_cols[i]:
            if st.button(tf, key=f"tf_{tf}", type="primary" if tf == timeframe else "secondary"):
                st.session_state.selected_timeframe = tf
                st.rerun()
    
    st.markdown("---")
    
    # Key metrics in a grid layout
    st.subheader("📊 Key Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        volume = data.get('volume', 0) or 0
        st.metric("Volume", f"{volume:,}")
    with metric_cols[1]:
        market_cap = data.get('market_cap', 0) or 0
        st.metric("Market Cap", f"${market_cap/1e9:.2f}B" if market_cap > 0 else "N/A")
    with metric_cols[2]:
        pe_ratio = data.get('pe_ratio', 0) or 0
        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio > 0 else "N/A")
    with metric_cols[3]:
        beta = data.get('beta', 0) or 0
        st.metric("Beta", f"{beta:.2f}" if beta != 0 else "N/A")
    
    # 52-week range
    range_cols = st.columns(2)
    with range_cols[0]:
        week_high = data.get('52_week_high', 0) or 0
        st.metric("52W High", f"${week_high:.2f}" if week_high > 0 else "N/A")
    with range_cols[1]:
        week_low = data.get('52_week_low', 0) or 0
        st.metric("52W Low", f"${week_low:.2f}" if week_low > 0 else "N/A")
    
    # Performance metrics
    performance_data = data.get('performance', {})
    if performance_data:
        st.subheader("📈 Performance")
        perf_cols = st.columns(len(performance_data))
        for i, (period, perf) in enumerate(performance_data.items()):
            with perf_cols[i]:
                perf_value = perf or 0
                color = "#00C851" if perf_value >= 0 else "#FF4444"
                st.markdown(f"<div style='text-align: center;'><h4>{period.upper()}</h4><h3 style='color: {color};'>{perf_value:+.2f}%</h3></div>", unsafe_allow_html=True)
    
    # Chart
    hist_data = data.get('hist', pd.DataFrame())
    if not hist_data.empty:
        st.subheader(f"📊 {timeframe} Price Chart")
        try:
            fig = px.line(
                hist_data,
                x=hist_data.index,
                y="Close",
                title=f"{data.get('name', 'Stock')} ({data.get('symbol', '')}) - {timeframe} Price Movement",
                labels={"Close": "Price ($)", "index": "Date"}
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price ($)",
                showlegend=False,
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not display chart: {str(e)}")
    else:
        st.info("📊 No historical data available for the selected timeframe.")
    
    # Additional technical indicators
    hist_data = data.get('hist', pd.DataFrame())
    if not hist_data.empty and len(hist_data) > 20:
        st.subheader("🔍 Technical Analysis")
        
        try:
            # Calculate moving averages
            hist_data_copy = hist_data.copy()
            hist_data_copy['MA20'] = hist_data_copy['Close'].rolling(window=20).mean()
            hist_data_copy['MA50'] = hist_data_copy['Close'].rolling(window=min(50, len(hist_data_copy))).mean()
            
            # Technical chart
            fig_tech = go.Figure()
            fig_tech.add_trace(go.Scatter(x=hist_data_copy.index, y=hist_data_copy['Close'], name='Price', line=dict(color='blue')))
            if not hist_data_copy['MA20'].isna().all():
                fig_tech.add_trace(go.Scatter(x=hist_data_copy.index, y=hist_data_copy['MA20'], name='MA20', line=dict(color='orange')))
            if not hist_data_copy['MA50'].isna().all():
                fig_tech.add_trace(go.Scatter(x=hist_data_copy.index, y=hist_data_copy['MA50'], name='MA50', line=dict(color='red')))
            
            fig_tech.update_layout(
                title=f"{data.get('name', 'Stock')} - Technical Analysis",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig_tech, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not display technical analysis: {str(e)}")
    elif not hist_data.empty:
        st.info("📊 Need more historical data (20+ days) for technical analysis.")

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = timeframe

# Use selected timeframe from buttons
if 'selected_timeframe' in st.session_state:
    timeframe = st.session_state.selected_timeframe

# Auto-refresh functionality
current_time = datetime.now()
time_diff = (current_time - st.session_state.last_update).total_seconds()

# Check if we should refresh (either by timer, stock change, or manual refresh)
should_refresh = (
    time_diff >= update_interval or 
    st.session_state.get('force_refresh', False) or
    'previous_stock' not in st.session_state
)

if should_refresh:
    st.session_state.last_update = current_time
    st.session_state.force_refresh = False  # Reset force refresh flag
    # Don't rerun here to avoid infinite loop

# Get and display comprehensive stock data
with st.spinner(f'Loading comprehensive data for {stock_symbol} ({timeframe})...'):
    data = get_comprehensive_stock_data(stock_symbol, timeframe)

if data:
    display_comprehensive_dashboard(data, timeframe)
else:
    st.error("❌ Unable to load stock data. Please try a different symbol.")

# Sidebar status
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Dashboard Status**")
st.sidebar.write(f"🕐 Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
st.sidebar.write(f"⏱️ Next update in: {max(0, update_interval - time_diff):.0f} seconds")
st.sidebar.write(f"📅 Current timeframe: {timeframe}")
st.sidebar.write(f"📈 Current stock: {stock_symbol}")
if data:
    st.sidebar.success(f"✅ {stock_symbol} data loaded successfully")
else:
    st.sidebar.error(f"❌ Failed to load {stock_symbol}")

# Auto-refresh timer (only if no manual changes)
if time_diff >= update_interval and not st.session_state.get('force_refresh', False):
    st.rerun()

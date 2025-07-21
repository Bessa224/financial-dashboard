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

# Tab navigation
tab1, tab2, tab3 = st.tabs(["📈 Individual Stock Analysis", "📊 All Stocks Table", "⚖️ Stock Comparison"])

# All stocks from your Excel spreadsheet
ALL_STOCKS = {
    "Bancos": ["ITUB4.SA", "BBDC4.SA", "SANB11.SA", "BBAS3.SA", "BPAC11.SA"],
    "Petróleo": ["PETR4.SA", "PETR3.SA", "PRIO3.SA", "RRRP3.SA"],
    "Mineração": ["VALE3.SA", "CSNA3.SA", "USIM5.SA", "GGBR4.SA"],
    "Tecnologia": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META"],
    "Varejo": ["MGLU3.SA", "LREN3.SA", "AMER3.SA", "VVAR3.SA"],
    "Telecomunicações": ["VIVT3.SA", "TIMS3.SA"],
    "Energia Elétrica": ["ELET3.SA", "ELET6.SA", "CPFE3.SA", "ENBR3.SA"],
    "Alimentício": ["JBSS3.SA", "BRFS3.SA", "MRFG3.SA"],
    "Papel e Celulose": ["SUZB3.SA", "KLBN11.SA"],
    "Siderurgia": ["GOAU4.SA", "CSNA3.SA"],
    "Construção": ["MRVE3.SA", "CYRE3.SA", "EZTC3.SA"]
}

# Function to get multiple stocks data
def get_all_stocks_data():
    """Get real-time data for all stocks in the portfolio"""
    all_data = []
    
    for sector, stocks in ALL_STOCKS.items():
        for symbol in stocks:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if info and info.get('regularMarketPrice'):
                    current_price = info.get('regularMarketPrice', 0) or 0
                    change = info.get('regularMarketChange', 0) or 0
                    change_percent = info.get('regularMarketChangePercent', 0) or 0
                    
                    # Get historical data for performance calculations
                    hist_5d = stock.history(period="5d")
                    hist_30d = stock.history(period="1mo")
                    hist_ytd = stock.history(period="ytd")
                    hist_1y = stock.history(period="1y")
                    
                    # Calculate performance
                    perf_5d = 0
                    perf_30d = 0
                    perf_ytd = 0
                    perf_1y = 0
                    
                    if not hist_5d.empty and len(hist_5d) > 1:
                        perf_5d = ((current_price - hist_5d['Close'].iloc[0]) / hist_5d['Close'].iloc[0] * 100)
                    if not hist_30d.empty:
                        perf_30d = ((current_price - hist_30d['Close'].iloc[0]) / hist_30d['Close'].iloc[0] * 100)
                    if not hist_ytd.empty:
                        perf_ytd = ((current_price - hist_ytd['Close'].iloc[0]) / hist_ytd['Close'].iloc[0] * 100)
                    if not hist_1y.empty:
                        perf_1y = ((current_price - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0] * 100)
                    
                    stock_data = {
                        'Setor': sector,
                        'Símbolo': symbol,
                        'Nome': info.get('longName', symbol)[:30] + '...' if len(info.get('longName', symbol)) > 30 else info.get('longName', symbol),
                        'Preço': current_price,
                        'Variação': change,
                        'Variação %': change_percent,
                        '5d %': perf_5d,
                        '30d %': perf_30d,
                        'YTD %': perf_ytd,
                        'LTM %': perf_1y,
                        'Volume': info.get('regularMarketVolume', 0) or 0,
                        'P/E': info.get('trailingPE', 0) or 0,
                        'Beta': info.get('beta', 0) or 0,
                        'Market Cap': info.get('marketCap', 0) or 0,
                        '52W High': info.get('fiftyTwoWeekHigh', 0) or 0,
                        '52W Low': info.get('fiftyTwoWeekLow', 0) or 0
                    }
                    all_data.append(stock_data)
            except Exception as e:
                continue  # Skip stocks that fail to load
    
    return pd.DataFrame(all_data)

# Function to style the dataframe
def style_dataframe(df):
    """Apply styling to the dataframe"""
    def color_negative_red(val):
        if isinstance(val, (int, float)):
            color = 'color: #FF4444' if val < 0 else 'color: #00C851' if val > 0 else 'color: #666'
            return color
        return ''
    
    # Apply styling (using .map instead of deprecated .applymap)
    styled_df = df.style.map(color_negative_red, subset=['Variação', 'Variação %', '5d %', '30d %', 'YTD %', 'LTM %'])
    
    # Format columns
    styled_df = styled_df.format({
        'Preço': 'R$ {:.2f}' if any('.SA' in symbol for symbol in df['Símbolo']) else '$ {:.2f}',
        'Variação': '{:+.2f}',
        'Variação %': '{:+.2f}%',
        '5d %': '{:+.2f}%',
        '30d %': '{:+.2f}%',
        'YTD %': '{:+.2f}%',
        'LTM %': '{:+.2f}%',
        'Volume': '{:,.0f}',
        'P/E': '{:.2f}',
        'Beta': '{:.2f}',
        'Market Cap': lambda x: f'${x/1e9:.2f}B' if x > 0 else 'N/A',
        '52W High': 'R$ {:.2f}' if any('.SA' in symbol for symbol in df['Símbolo']) else '$ {:.2f}',
        '52W Low': 'R$ {:.2f}' if any('.SA' in symbol for symbol in df['Símbolo']) else '$ {:.2f}'
    })
    
    return styled_df

# Function to compare two stocks
def compare_stocks(symbol1, symbol2, timeframe="1mo"):
    """Compare two stocks side by side"""
    try:
        stock1 = yf.Ticker(symbol1)
        stock2 = yf.Ticker(symbol2)
        
        info1 = stock1.info
        info2 = stock2.info
        
        # Get historical data
        hist1 = stock1.history(period=timeframe)
        hist2 = stock2.history(period=timeframe)
        
        if hist1.empty or hist2.empty:
            return None, None, None, None
        
        # Normalize prices for comparison (percentage change from start)
        hist1_norm = (hist1['Close'] / hist1['Close'].iloc[0] - 1) * 100
        hist2_norm = (hist2['Close'] / hist2['Close'].iloc[0] - 1) * 100
        
        return info1, info2, hist1_norm, hist2_norm
    except Exception as e:
        return None, None, None, None



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

# Tab 1: Individual Stock Analysis
with tab1:
    # Get and display comprehensive stock data
    with st.spinner(f'Loading comprehensive data for {stock_symbol} ({timeframe})...'):
        data = get_comprehensive_stock_data(stock_symbol, timeframe)
    
    if data:
        display_comprehensive_dashboard(data, timeframe)
    else:
        st.error("❌ Unable to load stock data. Please try a different symbol.")

# Tab 2: All Stocks Table
with tab2:
    st.subheader("📊 Portfolio Completo - Dados em Tempo Real")
    st.markdown("*Todos os ativos do seu portfólio com métricas financeiras atualizadas*")
    
    # Refresh button for the table
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Atualizar Dados", key="refresh_table"):
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", key="auto_refresh_table")
    
    # Load all stocks data
    with st.spinner('Carregando dados de todos os ativos...'):
        all_stocks_df = get_all_stocks_data()
    
    if not all_stocks_df.empty:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_stocks = len(all_stocks_df)
            st.metric("Total de Ativos", total_stocks)
        with col2:
            positive_stocks = len(all_stocks_df[all_stocks_df['Variação %'] > 0])
            st.metric("Em Alta", positive_stocks, f"{positive_stocks/total_stocks*100:.1f}%")
        with col3:
            negative_stocks = len(all_stocks_df[all_stocks_df['Variação %'] < 0])
            st.metric("Em Baixa", negative_stocks, f"{negative_stocks/total_stocks*100:.1f}%")
        with col4:
            avg_performance = all_stocks_df['Variação %'].mean()
            st.metric("Performance Média", f"{avg_performance:+.2f}%")
        
        st.markdown("---")
        
        # Sector filter with session state for better performance
        sectors = ['Todos'] + list(ALL_STOCKS.keys())
        if 'selected_sector' not in st.session_state:
            st.session_state.selected_sector = 'Todos'
        
        selected_sector = st.selectbox(
            "Filtrar por Setor:", 
            sectors, 
            index=sectors.index(st.session_state.selected_sector),
            key="sector_filter"
        )
        
        # Update session state
        st.session_state.selected_sector = selected_sector
        
        # Filter dataframe by sector (optimized)
        if selected_sector != 'Todos':
            filtered_df = all_stocks_df[all_stocks_df['Setor'] == selected_sector].copy()
        else:
            filtered_df = all_stocks_df.copy()
        
        # Display the styled table
        st.markdown("### 📈 Tabela de Ativos")
        
        # Make the table interactive
        styled_table = style_dataframe(filtered_df)
        st.dataframe(
            styled_table,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"portfolio_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        # Auto-refresh functionality for table (optimized)
        if auto_refresh:
            # Use placeholder for countdown instead of sleep
            placeholder = st.empty()
            for i in range(30, 0, -1):
                placeholder.text(f"Auto-refresh em {i} segundos...")
                time.sleep(1)
            placeholder.empty()
            st.rerun()
            
    else:
        st.error("❌ Não foi possível carregar os dados dos ativos. Tente novamente.")
        
    # Last update time for table
    st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

# Tab 3: Stock Comparison
with tab3:
    st.subheader("⚖️ Comparação de Ações")
    st.markdown("*Compare duas ações lado a lado com gráficos e métricas*")
    
    # Stock selection for comparison
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        stock1_symbol = st.selectbox(
            "Primeira Ação:",
            options=["AAPL", "GOOGL", "MSFT", "TSLA", "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA"],
            index=0,
            key="stock1_compare"
        )
    with col2:
        stock2_symbol = st.selectbox(
            "Segunda Ação:",
            options=["GOOGL", "AAPL", "MSFT", "TSLA", "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA"],
            index=0,
            key="stock2_compare"
        )
    with col3:
        comparison_timeframe = st.selectbox(
            "Período:",
            options=["5d", "1mo", "3mo", "6mo", "1y"],
            index=1,
            key="comparison_timeframe"
        )
    
    if st.button("🔄 Comparar Ações", key="compare_button"):
        if stock1_symbol != stock2_symbol:
            with st.spinner('Carregando dados para comparação...'):
                info1, info2, hist1_norm, hist2_norm = compare_stocks(stock1_symbol, stock2_symbol, comparison_timeframe)
            
            if info1 and info2 and hist1_norm is not None and hist2_norm is not None:
                # Display comparison metrics
                st.markdown("### 📊 Métricas Comparativas")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{stock1_symbol}** - {info1.get('longName', stock1_symbol)}")
                    price1 = info1.get('regularMarketPrice', 0) or 0
                    change1 = info1.get('regularMarketChangePercent', 0) or 0
                    pe1 = info1.get('trailingPE', 0) or 0
                    beta1 = info1.get('beta', 0) or 0
                    
                    st.metric("Preço", f"${price1:.2f}" if '.SA' not in stock1_symbol else f"R$ {price1:.2f}")
                    st.metric("Variação %", f"{change1:+.2f}%")
                    st.metric("P/E Ratio", f"{pe1:.2f}" if pe1 > 0 else "N/A")
                    st.metric("Beta", f"{beta1:.2f}" if beta1 > 0 else "N/A")
                
                with col2:
                    st.markdown(f"**{stock2_symbol}** - {info2.get('longName', stock2_symbol)}")
                    price2 = info2.get('regularMarketPrice', 0) or 0
                    change2 = info2.get('regularMarketChangePercent', 0) or 0
                    pe2 = info2.get('trailingPE', 0) or 0
                    beta2 = info2.get('beta', 0) or 0
                    
                    st.metric("Preço", f"${price2:.2f}" if '.SA' not in stock2_symbol else f"R$ {price2:.2f}")
                    st.metric("Variação %", f"{change2:+.2f}%")
                    st.metric("P/E Ratio", f"{pe2:.2f}" if pe2 > 0 else "N/A")
                    st.metric("Beta", f"{beta2:.2f}" if beta2 > 0 else "N/A")
                
                # Performance comparison chart
                st.markdown("### 📈 Comparação de Performance (Normalizada)")
                
                fig_comparison = go.Figure()
                
                fig_comparison.add_trace(go.Scatter(
                    x=hist1_norm.index,
                    y=hist1_norm.values,
                    mode='lines',
                    name=stock1_symbol,
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig_comparison.add_trace(go.Scatter(
                    x=hist2_norm.index,
                    y=hist2_norm.values,
                    mode='lines',
                    name=stock2_symbol,
                    line=dict(color='#ff7f0e', width=2)
                ))
                
                fig_comparison.update_layout(
                    title=f"Performance Comparison: {stock1_symbol} vs {stock2_symbol}",
                    xaxis_title="Data",
                    yaxis_title="Performance (%)",
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Performance summary
                perf1 = hist1_norm.iloc[-1]
                perf2 = hist2_norm.iloc[-1]
                
                st.markdown("### 🏆 Resumo de Performance")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(f"{stock1_symbol} Performance", f"{perf1:+.2f}%")
                with col2:
                    st.metric(f"{stock2_symbol} Performance", f"{perf2:+.2f}%")
                with col3:
                    winner = stock1_symbol if perf1 > perf2 else stock2_symbol
                    st.metric("Melhor Performance", winner)
                    
            else:
                st.error("❌ Erro ao carregar dados para comparação. Verifique os símbolos.")
        else:
            st.warning("⚠️ Selecione duas ações diferentes para comparar.")
    




# Sidebar status
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Dashboard Status**")
st.sidebar.write(f"🕐 Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
st.sidebar.write(f"⏱️ Next update in: {max(0, update_interval - time_diff):.0f} seconds")
st.sidebar.write(f"📅 Current timeframe: {timeframe}")
st.sidebar.write(f"📈 Current stock: {stock_symbol}")

# Show total stocks in portfolio
total_portfolio_stocks = sum(len(stocks) for stocks in ALL_STOCKS.values())
st.sidebar.write(f"📊 Portfolio: {total_portfolio_stocks} ativos")
st.sidebar.write(f"⚖️ Comparison: Available")

if 'data' in locals() and data:
    st.sidebar.success(f"✅ {stock_symbol} data loaded successfully")
else:
    st.sidebar.error(f"❌ Failed to load {stock_symbol}")

# Auto-refresh timer (only if no manual changes)
if time_diff >= update_interval and not st.session_state.get('force_refresh', False):
    st.rerun()

"""
AI Evaluation Dashboard
Advanced technical analysis with 11 indicators powered by Alpaca data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from ai.alpaca_trading_integration import get_alpaca_integration
from config import settings

# Page configuration
st.set_page_config(
    page_title="AI Evaluation - Market Alerts",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
    <style>
    .big-metric {
        font-size: 3rem !important;
        font-weight: bold;
        text-align: center;
    }
    .sentiment-strong-bullish {
        color: #00c853;
        background: linear-gradient(135deg, #00c853 0%, #64dd17 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sentiment-bullish {
        color: #4caf50;
        background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sentiment-neutral {
        color: #ff9800;
        background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sentiment-bearish {
        color: #f44336;
        background: linear-gradient(135deg, #f44336 0%, #e57373 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sentiment-strong-bearish {
        color: #c62828;
        background: linear-gradient(135deg, #c62828 0%, #d32f2f 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .indicator-card {
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .indicator-signal-bullish {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .indicator-signal-bearish {
        background: #ffebee;
        border-left: 4px solid #f44336;
    }
    .indicator-signal-neutral {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .level-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
    }
    .support-level {
        background: #e8f5e9;
        color: #2e7d32;
    }
    .resistance-level {
        background: #ffebee;
        color: #c62828;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'alpaca_integration' not in st.session_state:
    st.session_state.alpaca_integration = get_alpaca_integration()

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None


def get_sentiment_class(sentiment: str) -> str:
    """Get CSS class for sentiment"""
    sentiment_map = {
        "Strong Bullish": "sentiment-strong-bullish",
        "Bullish": "sentiment-bullish",
        "Neutral": "sentiment-neutral",
        "Bearish": "sentiment-bearish",
        "Strong Bearish": "sentiment-strong-bearish"
    }
    return sentiment_map.get(sentiment, "sentiment-neutral")


def get_signal_class(signal: str) -> str:
    """Get CSS class for indicator signal"""
    signal_lower = signal.lower()
    if any(word in signal_lower for word in ["bullish", "oversold", "rising"]):
        return "indicator-signal-bullish"
    elif any(word in signal_lower for word in ["bearish", "overbought", "falling"]):
        return "indicator-signal-bearish"
    else:
        return "indicator-signal-neutral"


def display_indicator_card(title: str, data: dict, emoji: str = "📊"):
    """Display a beautiful indicator card"""
    signal = data.get('signal', 'N/A')
    signal_class = get_signal_class(signal)

    st.markdown(f"""
        <div class="indicator-card {signal_class}">
            <h3>{emoji} {title}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Display indicator values
    for key, value in data.items():
        if key != 'signal' and not isinstance(value, dict):
            st.metric(key.replace('_', ' ').title(), f"{value}")

    # Display signal
    if signal != 'N/A':
        if "bullish" in signal.lower() or "oversold" in signal.lower():
            st.success(f"**Signal:** {signal}")
        elif "bearish" in signal.lower() or "overbought" in signal.lower():
            st.error(f"**Signal:** {signal}")
        else:
            st.warning(f"**Signal:** {signal}")


def show_analysis_header(analysis: dict):
    """Display analysis header with sentiment"""
    ticker = analysis['asset_analyzed']
    sentiment = analysis['overall_sentiment']
    summary = analysis['analysis_summary']

    # Title
    st.title(f"🤖 AI Evaluation: {ticker}")

    # Sentiment box
    sentiment_class = get_sentiment_class(sentiment)
    st.markdown(f"""
        <div class="{sentiment_class}">
            {sentiment}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Summary
    st.subheader("📝 Analysis Summary")
    st.info(summary)

    # Metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Source", "Alpaca")
    with col2:
        st.metric("Timeframe", analysis['data_timeframe'])
    with col3:
        st.metric("Data Points", analysis.get('data_points_analyzed', 0))
    with col4:
        timestamp = datetime.fromisoformat(analysis['analysis_timestamp_utc'].rstrip('Z'))
        st.metric("Analysis Time", timestamp.strftime('%H:%M UTC'))


def show_key_levels(analysis: dict):
    """Display support and resistance levels"""
    st.subheader("🎯 Key Price Levels")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Support Levels")
        for i, level in enumerate(analysis['key_levels']['support'], 1):
            st.markdown(f"""
                <div class="level-box support-level">
                    Support {i}: ${level:.2f}
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🔴 Resistance Levels")
        for i, level in enumerate(analysis['key_levels']['resistance'], 1):
            st.markdown(f"""
                <div class="level-box resistance-level">
                    Resistance {i}: ${level:.2f}
                </div>
            """, unsafe_allow_html=True)


def show_indicators_grid(indicators: dict):
    """Display all 11 indicators in a smart grid layout"""
    st.subheader("📊 Technical Indicators Analysis")

    # Row 1: Moving Averages (2 columns)
    st.markdown("### 📈 Trend Indicators")
    col1, col2 = st.columns(2)

    with col1:
        if 'sma' in indicators:
            display_indicator_card("Simple Moving Average (SMA)", indicators['sma'], "📉")

    with col2:
        if 'ema' in indicators:
            display_indicator_card("Exponential Moving Average (EMA)", indicators['ema'], "📊")

    st.markdown("---")

    # Row 2: Momentum Indicators (3 columns)
    st.markdown("### ⚡ Momentum Indicators")
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'macd' in indicators:
            display_indicator_card("MACD", indicators['macd'], "📶")

    with col2:
        if 'rsi' in indicators:
            display_indicator_card("RSI", indicators['rsi'], "🎚️")

    with col3:
        if 'stochastic' in indicators:
            display_indicator_card("Stochastic", indicators['stochastic'], "🔄")

    st.markdown("---")

    # Row 3: Volatility & Volume (3 columns)
    st.markdown("### 💨 Volatility & Volume Indicators")
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'bollinger_bands' in indicators:
            display_indicator_card("Bollinger Bands", indicators['bollinger_bands'], "📏")

    with col2:
        if 'obv' in indicators:
            display_indicator_card("On-Balance Volume", indicators['obv'], "📊")

    with col3:
        if 'vwap' in indicators:
            display_indicator_card("VWAP", indicators['vwap'], "💰")

    st.markdown("---")

    # Row 4: Advanced Indicators (3 columns)
    st.markdown("### 🎯 Advanced Indicators")
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'adx' in indicators:
            display_indicator_card("ADX (Trend Strength)", indicators['adx'], "💪")

    with col2:
        if 'ichimoku' in indicators:
            display_indicator_card("Ichimoku Cloud", indicators['ichimoku'], "☁️")

    with col3:
        if 'fibonacci' in indicators:
            display_indicator_card("Fibonacci Retracement", indicators['fibonacci'], "🔢")


def show_signals_summary(indicators: dict):
    """Display a summary of all signals"""
    st.subheader("🎯 Signals Summary")

    bullish = []
    bearish = []
    neutral = []

    for name, data in indicators.items():
        signal = data.get('signal', '')
        signal_lower = signal.lower()

        if any(word in signal_lower for word in ["bullish", "oversold", "rising"]):
            bullish.append(f"{name.upper()}: {signal}")
        elif any(word in signal_lower for word in ["bearish", "overbought", "falling"]):
            bearish.append(f"{name.upper()}: {signal}")
        else:
            neutral.append(f"{name.upper()}: {signal}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"### 🟢 Bullish ({len(bullish)})")
        for signal in bullish:
            st.write(f"• {signal}")

    with col2:
        st.error(f"### 🔴 Bearish ({len(bearish)})")
        for signal in bearish:
            st.write(f"• {signal}")

    with col3:
        st.warning(f"### 🟡 Neutral ({len(neutral)})")
        for signal in neutral:
            st.write(f"• {signal}")


def main():
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Analysis Settings")

        # Ticker selection
        ticker = st.text_input(
            "Stock Ticker",
            value="AAPL",
            help="Enter stock ticker symbol"
        ).upper()

        # Timeframe selection
        timeframe = st.selectbox(
            "Timeframe",
            options=["1D", "30D", "200D", "365D", "1H", "15m", "5m", "1m"],
            index=0,
            help="Select data timeframe"
        )

        # Force refresh option
        force_refresh = st.checkbox(
            "Force Refresh (Bypass Cache)",
            value=False,
            help="Fetch fresh data and recalculate analysis"
        )

        st.markdown("---")

        # Analyze button
        if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
            with st.spinner(f"Analyzing {ticker} ({timeframe})..."):
                analysis = st.session_state.alpaca_integration.get_ai_evaluation(
                    ticker,
                    timeframe,
                    force_refresh=force_refresh
                )
                st.session_state.current_analysis = analysis
                st.success("Analysis complete!")
                st.rerun()

        st.markdown("---")

        # Export button
        if st.session_state.current_analysis:
            if st.button("💾 Export to JSON", use_container_width=True):
                filepath = st.session_state.alpaca_integration.export_to_json(
                    st.session_state.current_analysis
                )
                if filepath:
                    st.success(f"Exported to: {filepath}")

                    # Show JSON preview
                    with st.expander("📄 JSON Preview"):
                        st.json(st.session_state.current_analysis)

        st.markdown("---")

        # Info
        st.info("""
        **💡 How it works:**

        1. Fetches data from Alpaca
        2. Calculates 11 technical indicators
        3. Analyzes signals & sentiment
        4. Caches results for 12 hours

        **📊 Indicators:**
        - SMA, EMA, MACD
        - RSI, Stochastic
        - Bollinger Bands
        - OBV, VWAP, ADX
        - Ichimoku, Fibonacci
        """)

    # Main content
    if st.session_state.current_analysis is None:
        # Welcome screen
        st.title("🤖 AI Evaluation Engine")
        st.markdown("### Advanced Technical Analysis with 11 Key Indicators")

        st.markdown("""
        Welcome to the AI Evaluation Engine! This powerful tool analyzes stocks using:

        - **11 Technical Indicators** - Comprehensive analysis from multiple perspectives
        - **Alpaca Data Integration** - Real-time data from Alpaca Markets
        - **Smart Caching** - 12-hour cache with end-of-day expiration
        - **JSON Export** - Export analysis for external use

        👈 **Get started:** Enter a ticker symbol and click "Run AI Analysis" in the sidebar
        """)

        # Show example
        with st.expander("📊 Example Analysis"):
            st.image("https://via.placeholder.com/800x400?text=AI+Analysis+Example", use_column_width=True)

    elif 'error' in st.session_state.current_analysis:
        # Error state
        st.error(f"❌ Analysis Error: {st.session_state.current_analysis['error']}")
        st.info("💡 Try selecting a different ticker or timeframe")

    else:
        # Display analysis
        analysis = st.session_state.current_analysis

        # Header with sentiment
        show_analysis_header(analysis)

        st.markdown("---")

        # Key levels
        show_key_levels(analysis)

        st.markdown("---")

        # Signals summary
        show_signals_summary(analysis['indicator_details'])

        st.markdown("---")

        # All indicators
        show_indicators_grid(analysis['indicator_details'])

        st.markdown("---")

        # Cache info
        st.caption(f"🕒 Analysis generated at: {analysis['analysis_timestamp_utc']}")
        st.caption("💾 Results cached for 12 hours or until end of trading day")


if __name__ == '__main__':
    main()

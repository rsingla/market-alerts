"""
Market Alerts Dashboard
Streamlit web interface for monitoring and configuring alerts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.market_hours import get_market_status
from data.market_data import get_market_summary
from data.news_fetcher import get_market_news
from data.technical_indicators import get_technical_analysis
from ai import get_analyzer
from ai.alpaca_trading_integration import get_alpaca_integration
from alerts.alert_engine import AlertEngine
from alerts.advanced_alert_engine import get_advanced_engine
from alerts.alert_rules import get_rules_manager, AlertRule, RuleType, RuleCondition
from alerts.alert_templates import AlertTemplates
from notifications import WhatsAppSender
from config import settings


# Page configuration
st.set_page_config(
    page_title="Market Alerts Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-metric {
        font-size: 2rem !important;
        font-weight: bold;
    }
    .positive {
        color: #00c853;
    }
    .negative {
        color: #ff1744;
    }
    .stAlert {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .indicator-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }

    /* AI Evaluation Styles */
    .sentiment-strong-bullish {
        background: linear-gradient(135deg, #00c853 0%, #64dd17 100%);
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .sentiment-bullish {
        background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .sentiment-neutral {
        background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .sentiment-bearish {
        background: linear-gradient(135deg, #f44336 0%, #e57373 100%);
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .sentiment-strong-bearish {
        background: linear-gradient(135deg, #c62828 0%, #d32f2f 100%);
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .indicator-card {
        padding: 12px;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin: 8px 0;
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
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .support-level {
        background: #e8f5e9;
        color: #2e7d32;
        border-left: 3px solid #2e7d32;
    }
    .resistance-level {
        background: #ffebee;
        color: #c62828;
        border-left: 3px solid #c62828;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'alert_engine' not in st.session_state:
    st.session_state.alert_engine = AlertEngine()

if 'whatsapp_sender' not in st.session_state:
    st.session_state.whatsapp_sender = WhatsAppSender()

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None

if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = get_analyzer()

if 'alpaca_integration' not in st.session_state:
    st.session_state.alpaca_integration = get_alpaca_integration()

if 'ai_evaluation_analysis' not in st.session_state:
    st.session_state.ai_evaluation_analysis = None

if 'advanced_engine' not in st.session_state:
    st.session_state.advanced_engine = get_advanced_engine()

if 'rules_manager' not in st.session_state:
    st.session_state.rules_manager = get_rules_manager()

# Initialize other notification senders for testing
if 'telegram_sender' not in st.session_state:
    try:
        from notifications.telegram_sender import TelegramSender
        st.session_state.telegram_sender = TelegramSender()
    except:
        st.session_state.telegram_sender = None

if 'email_sender' not in st.session_state:
    try:
        from notifications.email_sender import EmailSender
        st.session_state.email_sender = EmailSender()
    except:
        st.session_state.email_sender = None

if 'signal_sender' not in st.session_state:
    try:
        from notifications.signal_sender import SignalSender
        st.session_state.signal_sender = SignalSender()
    except:
        st.session_state.signal_sender = None


def show_market_status():
    """Display current market status"""
    status = get_market_status()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Trading Day", "Yes ✓" if status['is_trading_day'] else "No ✗")

    with col2:
        st.metric("Market Hours", "Open ✓" if status['is_market_hours'] else "Closed ✗")

    with col3:
        if status.get('time_to_close'):
            st.metric("Time to Close", status['time_to_close'])
        elif status.get('time_to_open'):
            st.metric("Time to Open", status['time_to_open'])
        else:
            st.metric("Market Status", "Closed")

    with col4:
        st.metric("Current Time", status['current_time'].split()[1])


def show_watchlist_summary():
    """Display watchlist with current prices"""
    st.subheader("📈 Watchlist Summary")

    with st.spinner("Fetching market data..."):
        quotes = get_market_summary()

    if not quotes:
        st.warning("No market data available. Check your API configuration.")
        st.info("💡 **Tip:** Make sure your Polygon.io API key is configured in .env")
        return

    # Create DataFrame
    data = []
    for symbol, quote in quotes.items():
        # Color coding for changes
        change_color = "🟢" if quote.change >= 0 else "🔴"

        data.append({
            'Symbol': symbol,
            'Price': f"${quote.price:.2f}",
            '': change_color,
            'Change %': f"{quote.change_percent:+.2f}%",
            'Change $': f"${quote.change:+.2f}",
            'Volume': f"{quote.volume:,}",
            'Vol Ratio': f"{quote.volume_ratio:.2f}x"
        })

    df = pd.DataFrame(data)

    # Display the dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.session_state.last_refresh = datetime.now()
    st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%I:%M:%S %p')} | Data from: Alpaca (primary) → Polygon.io → Yahoo Finance → Alpha Vantage")


def show_alerts():
    """Display current alerts"""
    st.subheader("🔔 Active Alerts")

    with st.spinner("Checking for alerts..."):
        alerts = st.session_state.alert_engine.check_markets()

    if not alerts:
        st.info("✓ No alerts at this time - all stocks within normal ranges")
        return

    # Display alerts by priority
    critical = [a for a in alerts if a.alert_level.value == 'critical']
    warning = [a for a in alerts if a.alert_level.value == 'warning']
    info = [a for a in alerts if a.alert_level.value == 'info']

    if critical:
        st.error(f"🚨 {len(critical)} Critical Alert{'s' if len(critical) > 1 else ''}")
        for alert in critical:
            with st.expander(f"{alert.symbol} - {alert.alert_type.value}", expanded=True):
                st.markdown(alert.message)

    if warning:
        st.warning(f"⚠️  {len(warning)} Warning Alert{'s' if len(warning) > 1 else ''}")
        for alert in warning:
            with st.expander(f"{alert.symbol} - {alert.alert_type.value}"):
                st.markdown(alert.message)

    if info:
        st.info(f"ℹ️ {len(info)} Info Alert{'s' if len(info) > 1 else ''}")
        for alert in info:
            with st.expander(f"{alert.symbol} - {alert.alert_type.value}"):
                st.markdown(alert.message)


def show_news():
    """Display market news"""
    st.subheader("📰 Market News")

    with st.spinner("Fetching latest news..."):
        articles = get_market_news(max_items=15)

    if not articles:
        st.info("No news available at this time")
        return

    for i, article in enumerate(articles, 1):
        with st.expander(f"{i}. {article.title}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Source:** {article.source}")
            with col2:
                st.markdown(f"**Published:** {article.published.strftime('%b %d, %I:%M %p')}")

            if article.summary:
                st.markdown(article.summary)
            st.markdown(f"[Read full article →]({article.url})")


def show_ai_analysis(symbol: str, quotes: dict):
    """Display AI-powered analysis for a stock"""
    st.subheader(f"🤖 AI Analysis for {symbol}")

    if symbol not in quotes:
        st.warning(f"No market data available for {symbol}")
        return

    quote = quotes[symbol]

    # Get technical indicators
    with st.spinner(f"Analyzing {symbol} with AI..."):
        try:
            # Fetch technical indicators
            technical_data = get_technical_analysis(symbol, period='3mo')

            if not technical_data or not technical_data.get('latest'):
                st.warning("Insufficient data for technical analysis")
                technical_data = {'latest': {}, 'signals': {}}

            # Prepare current data
            current_data = {
                'symbol': symbol,
                'price': quote.price,
                'change_percent': quote.change_percent,
                'volume': quote.volume,
                'day_high': quote.day_high,
                'day_low': quote.day_low,
            }

            # Get AI analysis
            analysis = st.session_state.ai_analyzer.analyze_stock(
                symbol=symbol,
                current_data=current_data,
                technical_indicators=technical_data,
                news=None  # Could add news context here
            )

            # Display AI summary
            st.info(f"**AI Summary:** {analysis['summary']}")

            # Full analysis in expander
            with st.expander("📊 Detailed Technical Analysis"):
                st.markdown(analysis['analysis'])

            # Recommendation
            rec = analysis['recommendation'].lower()
            if 'bullish' in rec:
                st.success(f"**💡 AI Recommendation:** {analysis['recommendation']}")
            elif 'bearish' in rec:
                st.error(f"**💡 AI Recommendation:** {analysis['recommendation']}")
            else:
                st.warning(f"**💡 AI Recommendation:** {analysis['recommendation']}")

        except Exception as e:
            st.error(f"AI Analysis Error: {str(e)}")
            st.info("💡 **Tip:** Make sure DEEPSEEK_API_KEY is configured in .env and has credits")


def show_price_chart(symbol: str):
    """Display price chart for a symbol"""
    from data.market_data import get_historical_data

    with st.spinner(f"Loading chart for {symbol}..."):
        hist = get_historical_data(symbol, period="1mo")

    if not hist:
        st.warning(f"No historical data available for {symbol}")
        return

    # Create candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=hist['dates'],
            open=hist['open'],
            high=hist['high'],
            low=hist['low'],
            close=hist['close'],
            name=symbol
        )
    ])

    fig.update_layout(
        title=f"{symbol} - Last 30 Days",
        yaxis_title="Price ($)",
        xaxis_title="Date",
        height=400,
        template="plotly_white",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)


def show_technical_indicators(symbol: str):
    """Display technical indicators for a stock"""
    st.subheader(f"📊 Technical Indicators - {symbol}")

    with st.spinner(f"Calculating indicators for {symbol}..."):
        indicators = get_technical_analysis(symbol, period='3mo')

    if not indicators or not indicators.get('latest'):
        st.warning(f"Insufficient data for technical analysis of {symbol}")
        return

    latest = indicators['latest']
    signals = indicators.get('signals', {})

    # Display key indicators in columns
    st.markdown("#### Key Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rsi = latest.get('rsi')
        if rsi:
            rsi_signal = signals.get('rsi', 'neutral')
            rsi_color = "🟢" if rsi_signal == 'oversold' else "🔴" if rsi_signal == 'overbought' else "🟡"
            st.metric("RSI (14)", f"{rsi:.2f} {rsi_color}", f"{rsi_signal.title()}")

    with col2:
        macd = latest.get('macd')
        if macd:
            macd_signal = signals.get('macd', 'neutral')
            macd_color = "🟢" if macd_signal == 'bullish' else "🔴"
            st.metric("MACD", f"{macd:.2f} {macd_color}", f"{macd_signal.title()}")

    with col3:
        sma_20 = latest.get('sma_20')
        if sma_20:
            st.metric("SMA 20", f"${sma_20:.2f}")

    with col4:
        bb_upper = latest.get('bb_upper')
        if bb_upper:
            st.metric("BB Upper", f"${bb_upper:.2f}")

    # Display all signals
    st.markdown("#### Trading Signals")
    signal_cols = st.columns(len(signals))

    for i, (key, value) in enumerate(signals.items()):
        with signal_cols[i]:
            if value == 'bullish' or value == 'oversold':
                st.success(f"**{key.replace('_', ' ').title()}**\n{value.title()}")
            elif value == 'bearish' or value == 'overbought':
                st.error(f"**{key.replace('_', ' ').title()}**\n{value.title()}")
            else:
                st.info(f"**{key.replace('_', ' ').title()}**\n{value.title()}")

    # Detailed indicators in expander
    with st.expander("📈 All Indicator Values"):
        ind_data = []
        for key, value in latest.items():
            if value is not None:
                ind_data.append({
                    'Indicator': key.replace('_', ' ').title(),
                    'Value': f"{value:.2f}"
                })
        if ind_data:
            st.dataframe(pd.DataFrame(ind_data), use_container_width=True, hide_index=True)


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
    if any(word in signal_lower for word in ["bullish", "oversold", "rising", "golden"]):
        return "indicator-signal-bullish"
    elif any(word in signal_lower for word in ["bearish", "overbought", "falling", "death"]):
        return "indicator-signal-bearish"
    else:
        return "indicator-signal-neutral"


def display_compact_indicator(title: str, data: dict, col):
    """Display a compact indicator card in a column"""
    signal = data.get('signal', 'N/A')
    signal_class = get_signal_class(signal)

    with col:
        st.markdown(f"""
            <div class="indicator-card {signal_class}">
                <div style="font-weight: bold; margin-bottom: 8px;">{title}</div>
            </div>
        """, unsafe_allow_html=True)

        # Show key values (limit to 2-3 most important)
        values_shown = 0
        for key, value in data.items():
            if key != 'signal' and not isinstance(value, dict) and values_shown < 3:
                st.caption(f"{key.replace('_', ' ').title()}: {value}")
                values_shown += 1

        # Show signal
        if signal != 'N/A':
            if "bullish" in signal.lower() or "oversold" in signal.lower():
                st.success(f"**{signal}**", icon="📈")
            elif "bearish" in signal.lower() or "overbought" in signal.lower():
                st.error(f"**{signal}**", icon="📉")
            else:
                st.warning(f"**{signal}**", icon="➡️")


def show_ai_evaluation_page():
    """Display AI Evaluation page with 11 indicators"""
    st.subheader("🤖 AI Trading Analysis Engine")
    st.caption("Advanced technical analysis with 11 key indicators powered by Alpaca data")

    # Controls in columns
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        ticker = st.text_input(
            "Stock Ticker",
            value="AAPL",
            help="Enter stock ticker symbol"
        ).upper()

    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            options=["1D", "30D", "200D", "365D", "1H", "15m", "5m", "1m"],
            index=0,
            help="Select data timeframe"
        )

    with col3:
        force_refresh = st.checkbox(
            "Force Refresh",
            value=False,
            help="Bypass 12hr cache"
        )

    with col4:
        if st.button("🚀 Analyze", type="primary", use_container_width=True):
            with st.spinner(f"Analyzing {ticker} ({timeframe})..."):
                analysis = st.session_state.alpaca_integration.get_ai_evaluation(
                    ticker,
                    timeframe,
                    force_refresh=force_refresh
                )
                st.session_state.ai_evaluation_analysis = analysis
                st.success("Analysis complete!")
                st.rerun()

    st.markdown("---")

    # Display analysis if available
    if st.session_state.ai_evaluation_analysis is None:
        # Welcome message
        st.info("""
        **Welcome to the AI Trading Analysis Engine!**

        This powerful tool analyzes stocks using 11 comprehensive technical indicators:
        - **Trend**: SMA, EMA
        - **Momentum**: MACD, RSI, Stochastic
        - **Volatility & Volume**: Bollinger Bands, OBV, VWAP
        - **Advanced**: ADX, Ichimoku Cloud, Fibonacci

        **Features:**
        - Real-time data from Alpaca Markets
        - Multiple timeframes: 1 day to 1 year (1D, 30D, 200D, 365D) + intraday (1H, 15m, 5m, 1m)
        - 12-hour intelligent caching
        - Automatic sentiment calculation
        - Support/resistance level identification

        👆 Enter a ticker symbol, select timeframe, and click "Analyze" to get started!
        """)
        return

    analysis = st.session_state.ai_evaluation_analysis

    # Check for errors
    if 'error' in analysis:
        st.error(f"Analysis Error: {analysis['error']}")
        st.info("💡 Try selecting a different ticker or timeframe")
        return

    # Header with sentiment
    ticker = analysis['asset_analyzed']
    sentiment = analysis['overall_sentiment']

    st.markdown(f"### 📊 Analysis: {ticker}")

    # Sentiment display
    sentiment_class = get_sentiment_class(sentiment)
    st.markdown(f"""
        <div class="{sentiment_class}">
            {sentiment}
        </div>
    """, unsafe_allow_html=True)

    # Metadata row
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

    st.markdown("---")

    # Summary
    with st.expander("📝 Analysis Summary", expanded=True):
        st.info(analysis['analysis_summary'])

    # Key Levels
    st.markdown("### 🎯 Key Price Levels")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🟢 Support Levels**")
        for i, level in enumerate(analysis['key_levels']['support'][:3], 1):
            st.markdown(f"""
                <div class="level-box support-level">
                    Support {i}: ${level:.2f}
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("**🔴 Resistance Levels**")
        for i, level in enumerate(analysis['key_levels']['resistance'][:3], 1):
            st.markdown(f"""
                <div class="level-box resistance-level">
                    Resistance {i}: ${level:.2f}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Signals Summary
    st.markdown("### 🎯 Signals Summary")
    indicators = analysis['indicator_details']

    bullish = []
    bearish = []
    neutral = []

    for name, data in indicators.items():
        signal = data.get('signal', '')
        signal_lower = signal.lower()

        if any(word in signal_lower for word in ["bullish", "oversold", "rising", "golden"]):
            bullish.append(f"{name.upper()}: {signal}")
        elif any(word in signal_lower for word in ["bearish", "overbought", "falling", "death"]):
            bearish.append(f"{name.upper()}: {signal}")
        else:
            neutral.append(f"{name.upper()}: {signal}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"**🟢 Bullish ({len(bullish)})**")
        for signal in bullish:
            st.caption(f"• {signal}")

    with col2:
        st.error(f"**🔴 Bearish ({len(bearish)})**")
        for signal in bearish:
            st.caption(f"• {signal}")

    with col3:
        st.warning(f"**🟡 Neutral ({len(neutral)})**")
        for signal in neutral:
            st.caption(f"• {signal}")

    st.markdown("---")

    # All Indicators in compact grid
    st.markdown("### 📊 Technical Indicators (11)")

    # Row 1: Trend (2 columns)
    st.markdown("**📈 Trend Indicators**")
    col1, col2 = st.columns(2)
    if 'sma' in indicators:
        display_compact_indicator("SMA (Simple Moving Average)", indicators['sma'], col1)
    if 'ema' in indicators:
        display_compact_indicator("EMA (Exponential Moving Average)", indicators['ema'], col2)

    st.markdown("---")

    # Row 2: Momentum (3 columns)
    st.markdown("**⚡ Momentum Indicators**")
    col1, col2, col3 = st.columns(3)
    if 'macd' in indicators:
        display_compact_indicator("MACD", indicators['macd'], col1)
    if 'rsi' in indicators:
        display_compact_indicator("RSI", indicators['rsi'], col2)
    if 'stochastic' in indicators:
        display_compact_indicator("Stochastic", indicators['stochastic'], col3)

    st.markdown("---")

    # Row 3: Volatility & Volume (3 columns)
    st.markdown("**💨 Volatility & Volume Indicators**")
    col1, col2, col3 = st.columns(3)
    if 'bollinger_bands' in indicators:
        display_compact_indicator("Bollinger Bands", indicators['bollinger_bands'], col1)
    if 'obv' in indicators:
        display_compact_indicator("OBV (On-Balance Volume)", indicators['obv'], col2)
    if 'vwap' in indicators:
        display_compact_indicator("VWAP", indicators['vwap'], col3)

    st.markdown("---")

    # Row 4: Advanced (3 columns)
    st.markdown("**🎯 Advanced Indicators**")
    col1, col2, col3 = st.columns(3)
    if 'adx' in indicators:
        display_compact_indicator("ADX (Trend Strength)", indicators['adx'], col1)
    if 'ichimoku' in indicators:
        display_compact_indicator("Ichimoku Cloud", indicators['ichimoku'], col2)
    if 'fibonacci' in indicators:
        display_compact_indicator("Fibonacci Retracement", indicators['fibonacci'], col3)

    st.markdown("---")

    # Export option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"🕒 Analysis generated at: {analysis['analysis_timestamp_utc']}")
        st.caption("💾 Results cached for 12 hours or until end of trading day")
    with col2:
        if st.button("💾 Export to JSON", use_container_width=True):
            filepath = st.session_state.alpaca_integration.export_to_json(analysis)
            if filepath:
                st.success(f"Exported to: {filepath}")


def show_test_panel():
    """Test panel for sending messages"""
    st.subheader("🧪 Test Panel")

    st.markdown("### Send Test Notifications")
    st.caption("Test each notification channel individually")

    message = st.text_area("Test Message", value="✅ Test message from Market Alerts Dashboard", height=100)

    # Create columns for each notification channel
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📧 Email", use_container_width=True):
            if not settings.BREVO_API_KEY:
                st.error("✗ Email not configured")
            else:
                with st.spinner("Sending email..."):
                    try:
                        from notifications.email_sender import send_message as send_email
                        success = send_email(
                            subject="Market Alerts Test",
                            body=message
                        )
                        if success:
                            st.success("✓ Email sent!")
                        else:
                            st.error("✗ Email failed")
                    except Exception as e:
                        st.error(f"✗ Error: {e}")

    with col2:
        if st.button("📱 WhatsApp", use_container_width=True):
            if not settings.TWILIO_ACCOUNT_SID:
                st.error("✗ WhatsApp not configured")
            else:
                with st.spinner("Sending WhatsApp..."):
                    success = st.session_state.whatsapp_sender.send_message(message)
                    if success:
                        st.success("✓ WhatsApp sent!")
                    else:
                        st.error("✗ WhatsApp failed")

    with col3:
        if st.button("✈️ Telegram", use_container_width=True):
            if not settings.TELEGRAM_BOT_TOKEN:
                st.error("✗ Telegram not configured")
            else:
                with st.spinner("Sending Telegram..."):
                    try:
                        from notifications.telegram_sender import send_message as send_telegram
                        success = send_telegram(message)
                        if success:
                            st.success("✓ Telegram sent!")
                        else:
                            st.error("✗ Telegram failed")
                            st.caption("Check Chat ID configuration")
                    except Exception as e:
                        st.error(f"✗ Error: {e}")

    with col4:
        if st.button("📡 Signal", use_container_width=True):
            if not settings.SIGNAL_SENDER_NUMBER:
                st.error("✗ Signal not configured")
            else:
                with st.spinner("Sending Signal..."):
                    try:
                        from notifications.signal_sender import send_message as send_signal
                        success = send_signal(message)
                        if success:
                            st.success("✓ Signal sent!")
                        else:
                            st.error("✗ Signal failed")
                    except Exception as e:
                        st.error(f"✗ Error: {e}")

    st.markdown("---")
    st.markdown("### Manual Alert Check")

    if st.button("🔍 Check Markets Now"):
        with st.spinner("Checking markets..."):
            alerts = st.session_state.alert_engine.check_markets()

        st.success(f"✓ Found {len(alerts)} alert{'s' if len(alerts) != 1 else ''}")

        if alerts:
            if st.button("📤 Send Alerts"):
                from notifications import send_alerts
                success = send_alerts(alerts, combine=True)
                if success:
                    st.success("✓ Alerts sent successfully!")
                else:
                    st.error("✗ Failed to send alerts")

    st.markdown("---")
    st.markdown("### System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**API Configuration:**")
        st.text(f"Alpaca Markets: {'✓' if settings.ALPACA_API_KEY and settings.ALPACA_API_KEY != 'your_alpaca_api_key' else '✗'}")
        st.text(f"Polygon.io: {'✓' if settings.POLYGON_API_KEY and settings.POLYGON_API_KEY != 'your_polygon_api_key' else '✗'}")
        st.text(f"Yahoo Finance: {'✓' if settings.USE_YFINANCE else '✗'}")
        st.text(f"Alpha Vantage: {'✓' if settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != 'your_alpha_vantage_key' else '✗'}")
        st.text(f"DeepSeek AI: {'✓' if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != 'your_deepseek_api_key' else '✗'}")

    with col2:
        st.markdown("**Notifications:**")
        st.text(f"Email (Brevo): {'✓' if settings.BREVO_API_KEY else '✗'}")
        st.text(f"Telegram: {'✓' if settings.TELEGRAM_BOT_TOKEN else '✗'}")
        st.text(f"Signal: {'✓' if settings.SIGNAL_SENDER_NUMBER else '✗'}")
        st.text(f"WhatsApp: {'✓' if settings.TWILIO_ACCOUNT_SID else '✗'}")


def show_advanced_alerts_page():
    """Display Advanced Alerts Management page"""
    st.subheader("🚨 Advanced Alert System")
    st.caption("Manage custom alert rules and view alert statistics")

    # Get statistics
    rules_manager = st.session_state.rules_manager
    advanced_engine = st.session_state.advanced_engine

    stats = advanced_engine.get_stats()

    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rules", stats['enabled_rules'])
    with col2:
        st.metric("Symbols Monitored", stats['symbols_with_rules'])
    with col3:
        st.metric("Cached Alerts", stats['cached_alerts'])
    with col4:
        scheduler_info = "✓ Running (30min)" if True else "✗ Stopped"
        st.metric("Scheduler", scheduler_info)

    st.markdown("---")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 All Rules", "➕ Add New Rule", "📊 Alert Templates"])

    with tab1:
        # Display all rules
        st.markdown("### Current Alert Rules")

        all_rules = rules_manager.get_all_rules()

        if not all_rules:
            st.info("No alert rules configured yet. Use the 'Add New Rule' tab to create your first rule!")
        else:
            # Create DataFrame for rules
            rules_data = []
            for rule in all_rules:
                status = "🟢 Enabled" if rule.enabled else "🔴 Disabled"
                rules_data.append({
                    'ID': rule.rule_id,
                    'Symbol': rule.symbol,
                    'Type': rule.rule_type.value,
                    'Condition': f"{rule.condition.value} {rule.threshold}",
                    'Status': status,
                    'Triggers': rule.trigger_count,
                    'Last Triggered': rule.last_triggered if rule.last_triggered else "Never",
                    'Description': rule.description
                })

            df = pd.DataFrame(rules_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### Manage Rules")

            # Rule management
            col1, col2 = st.columns([3, 1])
            with col1:
                rule_ids = [r.rule_id for r in all_rules]
                selected_rule_id = st.selectbox("Select Rule", rule_ids)

            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
                    if rules_manager.remove_rule(selected_rule_id):
                        st.success(f"✓ Deleted rule: {selected_rule_id}")
                        st.rerun()
                    else:
                        st.error(f"✗ Failed to delete rule")

            # Show selected rule details
            if selected_rule_id:
                selected_rule = rules_manager.get_rule(selected_rule_id)
                if selected_rule:
                    with st.expander("📝 Rule Details", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Symbol:** {selected_rule.symbol}")
                            st.write(f"**Type:** {selected_rule.rule_type.value}")
                            st.write(f"**Condition:** {selected_rule.condition.value}")
                            st.write(f"**Threshold:** {selected_rule.threshold}")
                        with col2:
                            st.write(f"**Enabled:** {'Yes' if selected_rule.enabled else 'No'}")
                            st.write(f"**Triggers:** {selected_rule.trigger_count}")
                            st.write(f"**Created:** {selected_rule.created_at}")
                            st.write(f"**Last Triggered:** {selected_rule.last_triggered if selected_rule.last_triggered else 'Never'}")

                        st.write(f"**Description:** {selected_rule.description}")

                        # Toggle enable/disable
                        if selected_rule.enabled:
                            if st.button("⏸️ Disable Rule", use_container_width=True):
                                if rules_manager.disable_rule(selected_rule_id):
                                    st.success("✓ Rule disabled")
                                    st.rerun()
                        else:
                            if st.button("▶️ Enable Rule", use_container_width=True):
                                if rules_manager.enable_rule(selected_rule_id):
                                    st.success("✓ Rule enabled")
                                    st.rerun()

    with tab2:
        # Add new rule
        st.markdown("### Create New Alert Rule")

        col1, col2 = st.columns(2)

        with col1:
            new_symbol = st.selectbox("Stock Symbol", settings.WATCHLIST, key="new_rule_symbol")
            new_rule_type = st.selectbox(
                "Alert Type",
                [
                    "price_threshold",
                    "price_change_percent",
                    "volume_spike",
                    "rsi_level",
                    "ma_crossover",
                    "bollinger_breakout",
                    "macd_signal",
                    "breaking_news"
                ],
                key="new_rule_type"
            )

        with col2:
            new_condition = st.selectbox(
                "Condition",
                ["above", "below", "crosses_above", "crosses_below", "greater_than", "less_than"],
                key="new_condition"
            )
            new_threshold = st.number_input(
                "Threshold Value",
                min_value=0.0,
                value=100.0,
                step=0.1,
                key="new_threshold"
            )

        new_description = st.text_input(
            "Description (optional)",
            placeholder="e.g., Alert when AAPL crosses above $200",
            key="new_description"
        )

        if st.button("➕ Create Rule", type="primary", use_container_width=True):
            # Generate rule ID
            import time
            rule_id = f"{new_symbol}_{new_rule_type}_{int(time.time())}"

            # Create rule
            new_rule = AlertRule(
                rule_id=rule_id,
                symbol=new_symbol,
                rule_type=RuleType(new_rule_type),
                condition=RuleCondition(new_condition),
                threshold=new_threshold,
                description=new_description if new_description else f"{new_symbol} {new_rule_type} rule"
            )

            if rules_manager.add_rule(new_rule):
                st.success(f"✓ Created new rule: {rule_id}")
                st.rerun()
            else:
                st.error("✗ Failed to create rule")

    with tab3:
        # Show alert templates
        st.markdown("### Alert Message Templates")
        st.caption("Preview how different alert types will look when sent")

        template_type = st.selectbox(
            "Select Template Type",
            [
                "Price Threshold",
                "Price Change %",
                "Volume Spike",
                "RSI Level",
                "MA Crossover",
                "Bollinger Breakout",
                "MACD Signal",
                "Breaking News",
                "Hourly Summary"
            ]
        )

        # Show template preview based on selection
        if template_type == "Price Threshold":
            msg = AlertTemplates.price_threshold_alert("AAPL", 305.50, 300.00, "above")
        elif template_type == "Price Change %":
            msg = AlertTemplates.price_change_percent_alert("TSLA", 250.75, 4.5, "30-minute")
        elif template_type == "Volume Spike":
            msg = AlertTemplates.volume_spike_alert("MSFT", 420.30, 150000000, 50000000, 3.0)
        elif template_type == "RSI Level":
            msg = AlertTemplates.rsi_alert("GOOGL", 180.25, 28.5, "oversold")
        elif template_type == "MA Crossover":
            msg = AlertTemplates.ma_crossover_alert("SPY", 580.25, "SMA", 200, "above")
        elif template_type == "Bollinger Breakout":
            msg = AlertTemplates.bollinger_breakout_alert("NVDA", 850.75, "upper", 845.00)
        elif template_type == "MACD Signal":
            msg = AlertTemplates.macd_signal_alert("META", 520.30, 1.5, -0.5, "bullish")
        elif template_type == "Breaking News":
            msg = AlertTemplates.breaking_news_alert("AAPL", "Apple announces major acquisition", "Reuters", ["acquisition"])
        else:  # Hourly Summary
            sample_stats = {
                'top_gainers': [
                    {'symbol': 'NVDA', 'price': 850.75, 'change_pct': 4.5},
                    {'symbol': 'TSLA', 'price': 250.30, 'change_pct': 3.2}
                ],
                'top_losers': [
                    {'symbol': 'AAPL', 'price': 195.20, 'change_pct': -2.1}
                ],
                'total_symbols': 69,
                'market_status': 'Open'
            }
            msg = AlertTemplates.hourly_summary(sample_stats)

        # Display template
        st.markdown("#### WhatsApp/Telegram Preview")
        st.info(msg['whatsapp'])

        with st.expander("📧 Email Preview"):
            st.markdown(f"**Subject:** {msg.get('email_subject', 'N/A')}")
            st.markdown(f"**Body:**\n\n{msg.get('email_body', 'N/A')}")

    st.markdown("---")

    # System status section
    st.markdown("### 📊 System Status")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Scheduler Information:**")
        st.text("Event-Driven Alerts: Every 30 minutes")
        st.text("Time-Based Summaries:")
        st.text("  • Morning News: 8:00 AM ET")
        st.text("  • Market Open: 9:35 AM ET")
        st.text("  • Hourly: 10 AM, 11 AM, 1 PM, 2 PM, 3 PM ET")
        st.text("  • Midday: 12:00 PM ET")
        st.text("  • Market Close: 4:05 PM ET")

    with col2:
        st.markdown("**Alert Types Available:**")
        for rule_type in RuleType:
            st.text(f"  • {rule_type.value}")


# Main app
def main():
    st.title("📊 Market Alerts Dashboard")
    st.markdown("---")

    # Market status (always visible)
    show_market_status()
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")

        page = st.radio(
            "Select Page",
            ["📊 Market Overview", "🤖 AI Evaluation (11 Indicators)", "📈 Analysis & Testing", "🚨 Advanced Alerts"]
        )

        st.markdown("---")

        st.header("Quick Stats")
        engine_stats = st.session_state.alert_engine.get_stats()
        sender_stats = st.session_state.whatsapp_sender.get_stats()

        st.metric("Total Alerts", engine_stats['total_alerts'])
        st.metric("Messages Sent", sender_stats['messages_sent'])

        st.markdown("---")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.last_refresh = None
            st.cache_data.clear()
            st.rerun()

        st.caption("💡 Refresh clears cache and fetches fresh data")

    # Main content
    if page == "📊 Market Overview":
        # Overview page: Watchlist + Alerts + News + AI

        # Watchlist Summary
        show_watchlist_summary()

        st.markdown("---")

        # Two columns for Alerts and News (displayed in parallel)
        col1, col2 = st.columns([1, 1])

        with col1:
            show_alerts()

        with col2:
            show_news()

    elif page == "🤖 AI Evaluation (11 Indicators)":
        # AI Evaluation page with all 11 indicators
        show_ai_evaluation_page()

    elif page == "📈 Analysis & Testing":
        # Analysis page: Charts + Technical Indicators + Test Panel

        st.subheader("📈 Technical Analysis")

        # Stock selector
        symbol = st.selectbox("Select Symbol", settings.WATCHLIST, key="chart_selector")

        if symbol:
            # Price chart
            show_price_chart(symbol)

            st.markdown("---")

            # Technical indicators
            show_technical_indicators(symbol)

            st.markdown("---")

        # Test panel
        show_test_panel()

    elif page == "🚨 Advanced Alerts":
        # Advanced Alerts page
        show_advanced_alerts_page()


if __name__ == '__main__':
    main()

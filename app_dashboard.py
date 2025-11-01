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
from alerts.alert_engine import AlertEngine
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
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'alert_engine' not in st.session_state:
    st.session_state.alert_engine = AlertEngine()

if 'whatsapp_sender' not in st.session_state:
    st.session_state.whatsapp_sender = WhatsAppSender()

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None


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
        st.warning("No market data available")
        return

    # Create DataFrame
    data = []
    for symbol, quote in quotes.items():
        data.append({
            'Symbol': symbol,
            'Price': f"${quote.price:.2f}",
            'Change': f"{quote.change_percent:+.2f}%",
            'Change $': f"${quote.change:+.2f}",
            'Volume': f"{quote.volume:,}",
            'Volume Ratio': f"{quote.volume_ratio:.2f}x"
        })

    df = pd.DataFrame(data)

    # Style the dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.session_state.last_refresh = datetime.now()
    st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%I:%M:%S %p')}")


def show_price_chart(symbol: str):
    """Display price chart for a symbol"""
    from data.market_data import get_historical_data

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
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def show_alerts():
    """Display current alerts"""
    st.subheader("🔔 Active Alerts")

    with st.spinner("Checking for alerts..."):
        alerts = st.session_state.alert_engine.check_markets()

    if not alerts:
        st.info("No alerts at this time")
        return

    # Display alerts by priority
    critical = [a for a in alerts if a.alert_level.value == 'critical']
    warning = [a for a in alerts if a.alert_level.value == 'warning']
    info = [a for a in alerts if a.alert_level.value == 'info']

    if critical:
        st.error(f"🚨 {len(critical)} Critical Alert{'s' if len(critical) > 1 else ''}")
        for alert in critical:
            with st.expander(f"{alert.symbol} - {alert.alert_type.value}"):
                st.markdown(alert.message)

    if warning:
        st.warning(f"⚠️ {len(warning)} Warning Alert{'s' if len(warning) > 1 else ''}")
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

    with st.spinner("Fetching news..."):
        articles = get_market_news(max_items=10)

    if not articles:
        st.info("No news available")
        return

    for i, article in enumerate(articles, 1):
        with st.expander(f"{i}. {article.title}"):
            st.markdown(f"**Source:** {article.source}")
            st.markdown(f"**Published:** {article.published.strftime('%B %d, %Y at %I:%M %p')}")
            if article.summary:
                st.markdown(article.summary)
            st.markdown(f"[Read more]({article.url})")


def show_settings():
    """Display and edit settings"""
    st.subheader("⚙️ Settings")

    st.markdown("### Alert Thresholds")

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Small Move (%)", value=float(settings.SMALL_MOVE_THRESHOLD), step=0.1, key="small_threshold")
        st.number_input("Medium Move (%)", value=float(settings.MEDIUM_MOVE_THRESHOLD), step=0.1, key="medium_threshold")
        st.number_input("Large Move (%)", value=float(settings.LARGE_MOVE_THRESHOLD), step=0.1, key="large_threshold")

    with col2:
        st.number_input("Volume Spike (x)", value=float(settings.VOLUME_SPIKE_THRESHOLD), step=0.1, key="volume_threshold")
        st.number_input("Check Interval (min)", value=int(settings.CHECK_INTERVAL_MINUTES), step=1, key="check_interval")

    st.markdown("### Watchlist")
    watchlist_text = st.text_area("Stock Symbols (comma-separated)", value=",".join(settings.WATCHLIST), height=100)

    st.markdown("### WhatsApp Notifications")
    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Twilio Account SID", value=settings.TWILIO_ACCOUNT_SID or "", type="password", disabled=True)
        st.text_input("WhatsApp From", value=settings.TWILIO_WHATSAPP_FROM or "", disabled=True)

    with col2:
        st.text_input("Twilio Auth Token", value="*" * 20 if settings.TWILIO_AUTH_TOKEN else "", type="password", disabled=True)
        st.text_input("WhatsApp To", value=settings.TWILIO_WHATSAPP_TO or "", disabled=True)

    st.info("To change these settings, edit the `.env` file and restart the application")


def show_test_panel():
    """Test panel for sending messages"""
    st.subheader("🧪 Test Panel")

    st.markdown("### Send Test Message")

    message = st.text_area("Message", value="This is a test message from Market Alerts Dashboard", height=100)

    if st.button("Send Test WhatsApp"):
        with st.spinner("Sending message..."):
            success = st.session_state.whatsapp_sender.send_message(message)

        if success:
            st.success("✓ Test message sent successfully!")
        else:
            st.error("✗ Failed to send message. Check logs for details.")

    st.markdown("### Manual Alert Check")

    if st.button("Check Markets Now"):
        with st.spinner("Checking markets..."):
            alerts = st.session_state.alert_engine.check_markets()

        st.success(f"✓ Found {len(alerts)} alerts")

        if alerts:
            if st.button("Send Alerts via WhatsApp"):
                from notifications import send_alerts
                success = send_alerts(alerts, combine=True)
                if success:
                    st.success("✓ Alerts sent successfully!")
                else:
                    st.error("✗ Failed to send alerts")


# Main app
def main():
    st.title("📊 Market Alerts Dashboard")
    st.markdown("---")

    # Market status
    show_market_status()
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")

        page = st.radio(
            "Select Page",
            ["Overview", "Alerts", "News", "Charts", "Settings", "Test Panel"]
        )

        st.markdown("---")

        st.header("Quick Stats")
        engine_stats = st.session_state.alert_engine.get_stats()
        sender_stats = st.session_state.whatsapp_sender.get_stats()

        st.metric("Total Alerts", engine_stats['total_alerts'])
        st.metric("Messages Sent", sender_stats['messages_sent'])

        st.markdown("---")

        if st.button("🔄 Refresh Data"):
            st.session_state.last_refresh = None
            st.rerun()

    # Main content
    if page == "Overview":
        show_watchlist_summary()

    elif page == "Alerts":
        show_alerts()

    elif page == "News":
        show_news()

    elif page == "Charts":
        st.subheader("📈 Price Charts")
        symbol = st.selectbox("Select Symbol", settings.WATCHLIST)
        if symbol:
            show_price_chart(symbol)

    elif page == "Settings":
        show_settings()

    elif page == "Test Panel":
        show_test_panel()


if __name__ == '__main__':
    main()

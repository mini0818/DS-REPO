import streamlit as st
import requests
import yfinance as yf
from datetime import date

# ===== Replace with your Finnhub API key =====
FINNHUB_API_KEY = "d28sglhr01qle9gsjmrgd28sglhr01qle9gsjms0"

def search_tickers(query):
    """Search tickers and companies from Finnhub API"""
    url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("result", [])
    else:
        st.error("Error fetching ticker search results.")
        return []

# --- Streamlit app starts here ---
st.set_page_config(page_title="📈 Stock Price App with Live Search", layout="centered")

st.title("📊 Stock Price App with Live Company Search")

query = st.text_input("Type company name or ticker:")

tickerSymbol = None
if query:
    results = search_tickers(query)
    if results:
        options = [f"{item['description']} ({item['symbol']})" for item in results]
        selected = st.selectbox("Select the company:", options)
        tickerSymbol = selected.split("(")[-1].replace(")", "")
    else:
        st.warning("No matching companies found.")

if tickerSymbol:
    start_date = st.date_input("Start Date", date(2023, 1, 1))
    end_date = st.date_input("End Date", date.today())

    if start_date >= end_date:
        st.error("❌ End date must be after start date.")
    else:
        try:
            tickerData = yf.Ticker(tickerSymbol)
            tickerDf = tickerData.history(start=start_date, end=end_date)

            if tickerDf.empty:
                st.warning("⚠️ No data available for this ticker and date range.")
            else:
                # Company info expander
                with st.expander("📌 Company Info"):
                    info = tickerData.info
                    logo_url = info.get('logo_url')
                    if logo_url:
                        st.image(logo_url, width=120)
                    st.write(f"**Name:** {info.get('longName', 'N/A')}")
                    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                    website = info.get('website')
                    if website:
                        st.write(f"**Website:** [{website}]({website})")

                # Closing Price
                st.subheader("📉 Closing Price")
                st.line_chart(tickerDf['Close'])

                # Volume
                st.subheader("📦 Volume Traded")
                st.line_chart(tickerDf['Volume'])

                # 20-day Moving Average
                tickerDf['MA20'] = tickerDf['Close'].rolling(window=20).mean()
                st.subheader("📈 20-Day Moving Average")
                st.line_chart(tickerDf[['Close', 'MA20']])

                # Summary Stats
                st.subheader("📊 Summary Statistics")
                st.write(f"**Max Closing Price:** ${tickerDf['Close'].max():.2f}")
                st.write(f"**Min Closing Price:** ${tickerDf['Close'].min():.2f}")
                st.write(f"**Average Volume:** {tickerDf['Volume'].mean():,.0f}")

        except Exception as e:
            st.error(f"⚠️ Something went wrong fetching data: {e}")

else:
    st.info("Start typing a company name or ticker to search.")

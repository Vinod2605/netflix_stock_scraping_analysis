# Netflix Stock Data: Web Scraping and Analysis
# Goal: scrape Netflix share price data from a web page, clean it, and study the trends.
# Tip: each chart opens in a window. Close the window to continue the program.

import os
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

# Folder to save the charts (used later in the README)
os.makedirs("images", exist_ok=True)

# ---------------------------------------------------------
# Step 1: Scrape the price table from the web page
# ---------------------------------------------------------
url = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/"
    "netflix_data_webpage.html"
)
html_data = requests.get(url).text
soup = BeautifulSoup(html_data, "html.parser")

# Find the table and read each row
table = soup.find("table")
rows = []
for row in table.find_all("tr"):
    cells = row.find_all("td")
    # A normal price row has 7 cells. Other rows (like dividends) are skipped.
    if len(cells) >= 7:
        rows.append({
            "Date": cells[0].text.strip(),
            "Open": cells[1].text.strip(),
            "High": cells[2].text.strip(),
            "Low": cells[3].text.strip(),
            "Close": cells[4].text.strip(),
            "Volume": cells[6].text.strip(),   # cells[5] is Adj Close, which we do not need
        })

netflix = pd.DataFrame(rows)
print("Raw scraped data (first 5 rows):")
print(netflix.head())

# ---------------------------------------------------------
# Step 2: Clean the data
# ---------------------------------------------------------
# Change the dates from text to real dates
netflix["Date"] = pd.to_datetime(netflix["Date"], errors="coerce")

# Remove commas (like "1,234") and change the prices to numbers
for column in ["Open", "High", "Low", "Close", "Volume"]:
    netflix[column] = netflix[column].str.replace(",", "", regex=False)
    netflix[column] = pd.to_numeric(netflix[column], errors="coerce")

# Remove rows that could not be converted, then put the oldest date first
netflix = netflix.dropna()
netflix = netflix.sort_values("Date").reset_index(drop=True)

# ---------------------------------------------------------
# Step 3: Add useful columns
# ---------------------------------------------------------
# Daily return = how much the price changed since the day before (in %)
netflix["Daily Return %"] = netflix["Close"].pct_change() * 100

# 50-day average = the average closing price of the last 50 days (shows the trend)
netflix["50-Day Average"] = netflix["Close"].rolling(window=50).mean()

# ---------------------------------------------------------
# Step 4: Summary numbers
# ---------------------------------------------------------
highest = netflix.loc[netflix["Close"].idxmax()]
lowest = netflix.loc[netflix["Close"].idxmin()]

print("\n--- Summary ---")
print("Period:", netflix["Date"].min().date(), "to", netflix["Date"].max().date())
print("Trading days:", len(netflix))
print("Highest close:", round(highest["Close"], 2), "on", highest["Date"].date())
print("Lowest close:", round(lowest["Close"], 2), "on", lowest["Date"].date())
print("Average daily return:", round(netflix["Daily Return %"].mean(), 3), "%")
print("Volatility (std. dev. of daily return):", round(netflix["Daily Return %"].std(), 3), "%")

# ---------------------------------------------------------
# Step 5: Chart 1 - closing price with 50-day average
# ---------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(netflix["Date"], netflix["Close"], label="Closing Price", color="blue", alpha=0.6)
plt.plot(netflix["Date"], netflix["50-Day Average"], label="50-Day Average", color="red")
plt.xlabel("Date")
plt.ylabel("Price (US$)")
plt.title("Netflix - Closing Price and 50-Day Average")
plt.legend()
plt.savefig("images/netflix_closing_price.png", dpi=150, bbox_inches="tight")
plt.show()

# ---------------------------------------------------------
# Step 6: Chart 2 - trading volume
# ---------------------------------------------------------
plt.figure(figsize=(12, 5))
plt.plot(netflix["Date"], netflix["Volume"], color="green")
plt.xlabel("Date")
plt.ylabel("Shares Traded")
plt.title("Netflix - Trading Volume")
plt.savefig("images/netflix_trading_volume.png", dpi=150, bbox_inches="tight")
plt.show()

# ---------------------------------------------------------
# Step 7: Chart 3 - how daily returns are spread out
# ---------------------------------------------------------
plt.figure(figsize=(9, 5))
sns.histplot(netflix["Daily Return %"].dropna(), bins=50, color="blue")
plt.xlabel("Daily Return (%)")
plt.ylabel("Number of Days")
plt.title("Netflix - Distribution of Daily Returns")
plt.savefig("images/netflix_daily_returns.png", dpi=150, bbox_inches="tight")
plt.show()


import requests
from bs4 import BeautifulSoup
import csv

url = "https://windrun.io/abilities"

# Pretend to be a browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", {"id": "ability-stats"})
rows = table.find("tbody").find_all("tr")

with open("dota2_abilities.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Ability", "Pick %", "Win %", "Avg Pick #", "Value"])

    for row in rows:
        cols = row.find_all("td")
        ability = cols[1].get_text(strip=True)
        pick_perc = cols[2].get_text(strip=True)
        win_perc = cols[3].get_text(strip=True)
        avg_pick = cols[4].get_text(strip=True)
        value = cols[5].get_text(strip=True)
        writer.writerow([ability, pick_perc, win_perc, avg_pick, value])

print("✅ Data scraped and saved to dota2_abilities.csv")

import requests
from bs4 import BeautifulSoup
import csv

url = "https://windrun.io/ability-pairs"

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

# Find the table by its ID
table = soup.find("table", {"id": "ability-pair-stats"})
rows = table.find("tbody").find_all("tr")

with open("dota2_ability_pairs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Ability One", "Ability One Win %", 
        "Ability Two", "Ability Two Win %",
        "Sample Size", "Combined Win %", "Synergy Δ"
    ])

    for row in rows:
        cols = row.find_all("td")

        ability_one_name = cols[1].get_text(strip=True)
        ability_one_win = cols[2].get_text(strip=True)
        ability_two_name = cols[4].get_text(strip=True)
        ability_two_win = cols[5].get_text(strip=True)
        sample_size = cols[6].get_text(strip=True)
        combined_win = cols[7].get_text(strip=True)
        synergy_delta = cols[8].get_text(strip=True)

        writer.writerow([
            ability_one_name, ability_one_win,
            ability_two_name, ability_two_win,
            sample_size, combined_win, synergy_delta
        ])

print("✅ Ability pair data saved to dota2_ability_pairs.csv")

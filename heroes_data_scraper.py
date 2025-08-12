import requests
from bs4 import BeautifulSoup
import csv

url = "https://windrun.io/ability-by-hero"

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

# Find the hero table
table = soup.find("table", {"id": "ability-stats"})
rows = table.find("tbody").find_all("tr")

with open("dota2_hero_abilities.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Hero", "Ability 1", "Ability 2", "Ability 3", "Ability 4"])

    for row in rows:
        cols = row.find_all("td")

        # Hero name
        hero = cols[1].find("a").get_text(strip=True)

        # Ability names (inside the 3rd <td>)
        ability_links = cols[2].find_all("a")
        abilities = [a.get_text(strip=True) for a in ability_links]

        # Keep only first 4 abilities
        abilities = abilities[:4]

        writer.writerow([hero] + abilities)

print("✅ Saved hero abilities to dota2_hero_abilities.csv")

import pandas as pd
import streamlit as st

# === Load data ===
abilities_df = pd.read_csv("dota2_abilities.csv")  # Ability, Pick %, Win %, Avg Pick #, Value
pairs_df = pd.read_csv("dota2_ability_pairs.csv")  # Ability One, Ability One Win %, Ability Two, Ability Two Win %, Sample Size, Combined Win %, Synergy Δ
hero_abilities_df = pd.read_csv("dota2_hero_abilities.csv")  # Hero, Ability 1, Ability 2, Ability 3, Ability 4

def normalize_name(name):
    if not isinstance(name, str) or name.strip() == "":
        return ""  # treat missing/empty as empty string
    return name.strip().lower()


abilities_df["Ability_norm"] = abilities_df["Ability"].apply(normalize_name)
pairs_df["Ability One_norm"] = pairs_df["Ability One"].apply(normalize_name)
pairs_df["Ability Two_norm"] = pairs_df["Ability Two"].apply(normalize_name)
for col in ["Ability 1", "Ability 2", "Ability 3", "Ability 4"]:
    hero_abilities_df[col + "_norm"] = hero_abilities_df[col].apply(normalize_name)

# === UI ===
st.title("Dota 2 Ability Draft Assistant")
# Drop NaNs and convert to strings before sorting
hero_abilities_df["Hero"] = hero_abilities_df["Hero"].fillna("").astype(str).str.strip()
hero_names_sorted = sorted(hero_abilities_df["Hero"].unique())

# Hero pool input
hero_pool = st.multiselect(
    "Select heroes in the current pool",
    sorted(hero_abilities_df["Hero"].unique())
)

# Drafted abilities input
drafted_hero = st.selectbox("Select your drafted hero (optional)", [""] + sorted(hero_abilities_df["Hero"].unique()))
drafted_abilities = st.multiselect("Select your drafted abilities (up to 4)", abilities_df["Ability"].unique())

# === Step 1: Get available abilities from hero pool ===
# Only proceed if heroes are selected
if not hero_pool:
    st.write("Please select at least one hero from the pool.")
else:
    available_rows = hero_abilities_df[hero_abilities_df["Hero"].isin(hero_pool)]
    available_abilities = []

    # Step 1: Build a DataFrame of abilities with heroes from filtered rows
    available_abilities = []
    for _, row in available_rows.iterrows():
        for i in range(1, 5):
            ability_raw = row.get(f"Ability {i}", "")
            ability_name = ability_raw if isinstance(ability_raw, str) else ""
            ability_name = ability_name.strip()
            if ability_name == "":
                continue  # skip empty abilities
            available_abilities.append({
                "Hero": row["Hero"],
                "Ability": ability_name
            })

    available_df = pd.DataFrame(available_abilities)

    # === Step 2: Define helper functions ===
    def get_top_synergies(ability):
        norm_name = normalize_name(ability)
        mask = (pairs_df["Ability One_norm"] == norm_name) | (pairs_df["Ability Two_norm"] == norm_name)
        related = pairs_df[mask].copy()
        # Get partner ability name
        def partner(row):
            if row["Ability One_norm"] == norm_name:
                return row["Ability Two"]
            else:
                return row["Ability One"]
        related["Partner"] = related.apply(partner, axis=1)
        return ", ".join(related.sort_values("Synergy Δ", ascending=False)["Partner"].head(3))

    def adjusted_win_percent(row):
        base_win = float(str(row["Win %"]).replace("%", "")) if pd.notnull(row["Win %"]) else None
        if not drafted_abilities or base_win is None:
            return base_win
        total_delta = 0
        for drafted in drafted_abilities:
            norm_a = normalize_name(row["Ability"])
            norm_b = normalize_name(drafted)
            pair_row = pairs_df[
                ((pairs_df["Ability One_norm"] == norm_a) & (pairs_df["Ability Two_norm"] == norm_b)) |
                ((pairs_df["Ability Two_norm"] == norm_a) & (pairs_df["Ability One_norm"] == norm_b))
            ]
            if not pair_row.empty:
                delta_str = str(pair_row.iloc[0]["Synergy Δ"]).replace("%", "")
                try:
                    total_delta += float(delta_str)
                except ValueError:
                    pass
        return round(base_win + total_delta, 2)

    # === Step 3: Process and display results ===
    # Only proceed if we have data
    if not available_df.empty:
        available_df["Ability_norm"] = available_df["Ability"].apply(normalize_name)
        
        # Merge with abilities data to get win percentages
        # Use suffixes to avoid column conflicts
        merged_df = available_df.merge(
            abilities_df[["Ability", "Win %", "Ability_norm"]],
            left_on="Ability_norm",
            right_on="Ability_norm",
            how="left",
            suffixes=('', '_abilities')
        )
        
        # Drop duplicate columns if they exist
        if "Ability_abilities" in merged_df.columns:
            merged_df.drop(columns="Ability_abilities", inplace=True)
        
        # Ensure we have the correct columns before proceeding
        if "Ability" not in merged_df.columns:
            st.error(f"Missing 'Ability' column. Available columns: {list(merged_df.columns)}")
        else:
            # Add synergies and adjusted win percentages
            merged_df["Top 3 Synergies"] = merged_df["Ability"].apply(get_top_synergies)
            merged_df["Adjusted Win %"] = merged_df.apply(adjusted_win_percent, axis=1)
            
            # Display the results
            st.dataframe(merged_df[["Hero", "Ability", "Win %", "Adjusted Win %", "Top 3 Synergies"]])
    else:
        st.write("No abilities available for the selected hero pool.")

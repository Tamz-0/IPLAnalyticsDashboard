import pandas as pd

df = pd.read_csv("data/raw/IPL.csv")

print("Columns in your CSV:")
print(df.columns.tolist())
print()

name_cols = ["batter", "bowler", "player_out", "striker", "non_striker"]
existing_cols = [c for c in name_cols if c in df.columns]

print(f"Name columns found: {existing_cols}")
print()

all_names = set()
for col in existing_cols:
    all_names.update(df[col].dropna().unique())

all_names = sorted(all_names)

print(f"Total unique player names: {len(all_names)}")
print()

while True:
    keyword = input("Enter player name to search (or 'quit' to exit, 'all' to dump all names): ").strip().lower()
    
    if keyword == "quit":
        break
    
    elif keyword == "all":
        print("\n--- ALL PLAYER NAMES ---")
        for name in all_names:
            print(name)
        print()
    
    else:
        matches = [n for n in all_names if keyword in n.lower()]
        
        if matches:
            print(f"\nMatches for '{keyword}':")
            for i, name in enumerate(matches, 1):
                print(f"  {i}. {name}")
            print()
        else:
            print(f"  No matches found for '{keyword}'\n")
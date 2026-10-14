from database import register_player_and_score, get_leaderboard, update_player_username

print("--- 1. Testing Create & Save Score ---")
register_player_and_score("Maicah", 1500)
register_player_and_score("Cate", 2500)

print("\n--- 2. Testing Update Profile ---")
update_player_username("Maicah", "Maicah_Rubz")

print("\n--- 3. Testing Read (Leaderboard) ---")
top_players = get_leaderboard(5)
for rank, entry in enumerate(top_players, start=1):
    print(f"Rank {rank}: {entry['username']} - {entry['score']} pts")
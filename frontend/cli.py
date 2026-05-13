import requests
import time

SERVER_IP = input("Enter server IP address: ").strip()
BASE = f"http://{SERVER_IP}:8000"

def draw_board(board):
    def val(x, i):
        return x if x else str(i)

    print()
    print(f"{val(board[0],0)} | {val(board[1],1)} | {val(board[2],2)}")
    print("---------")
    print(f"{val(board[3],3)} | {val(board[4],4)} | {val(board[5],5)}")
    print("---------")
    print(f"{val(board[6],6)} | {val(board[7],7)} | {val(board[8],8)}")
    print()

def print_stats(state):
    print("\n=== STATISTICS ===")
    print(f"{'Player':<15}{'W':<5}{'L':<5}{'D':<5}")
    print("-" * 30)

    for name, stats in state["statistics"].items():
        print(f"{name:<15}{stats['wins']:<5}{stats['losses']:<5}{stats['draws']:<5}")

    print("-" * 30 + "\n")

def print_players(state):
    print("\n=== PLAYERS ===")

    for p in state["players"]:
        print("-", p)

def print_matches(state):
    print("\n=== MATCHES ===")

    for m in state["matches"]:
        print(
            f"ID: {m['id']} Players: {m['players']} Winner: {m.get('winner')}"
        )

def fetch_match(match_id):
    return requests.get(f"{BASE}/match/{match_id}").json()

def play_match(match_id, player_name):
    while True:
        match = fetch_match(match_id)

        print("\n" * 5)
        draw_board(match["board"])

        if match.get("winner"):
            print(f"Winner: {match['winner']}")
            break

        if match.get("is_draw"):
            print("Draw!")
            break

        print(f"Current turn: {match['current_player']}")

        if match["current_player"] != player_name:
            print("Waiting for opponent move...")
            time.sleep(2)
            continue

        pos = input("Choose position (0-8) or q to quit: ")

        if pos == "q":
            break

        try:
            pos = int(pos)
        except:
            print("Invalid input")
            continue

        res = requests.post(
            f"{BASE}/updateMatch",
            json={
                "match_id": match_id,
                "position": pos,
                "player": player_name,
            },
        )

        if res.status_code != 200:
            print(res.json())
            time.sleep(1)
            continue

def menu():
    print("\n=== TIC TAC TOE CLI ===")
    print("1. Create player")
    print("2. Start match")
    print("3. Join existing match")
    print("4. Show stats")
    print("5. Show players")
    print("6. Show matches")
    print("7. Delete player")
    print("0. Exit")

while True:
    menu()
    choice = input("Choice: ").strip()

    try:
        if choice == "1":
            name = input("Name: ")
            res = requests.post(f"{BASE}/createPlayer", json={"name": name})
            print(res.json())

        elif choice == "2":
            player_name = input("Your player name: ")

            res = requests.post(
                f"{BASE}/startMatch",
                params={"player_name": player_name},
            )

            if res.status_code != 200:
                print(res.json())
                continue

            match = res.json()

            print(f"Match created!")
            print(f"Match ID: {match['id']}")
            print("Waiting for opponent to join...")

            while True:
                current = fetch_match(match["id"])

                if current.get("started"):
                    print(f"Opponent joined: {current['players'][1]}")
                    break

                time.sleep(2)

            play_match(match["id"], player_name)
            
        elif choice == "3":
            player_name = input("Your player name: ")
            match_id = int(input("Match ID: "))

            res = requests.post(
                f"{BASE}/joinMatch",
                params={
                    "match_id": match_id,
                    "player_name": player_name,
                },
            )

            if res.status_code != 200:
                print(res.json())
                continue

            print(res.json()["message"])

            play_match(match_id, player_name)
            
        elif choice == "4":
            state = requests.get(f"{BASE}/state").json()
            print_stats(state)

        elif choice == "5":
            state = requests.get(f"{BASE}/state").json()
            print_players(state)

        elif choice == "6":
            state = requests.get(f"{BASE}/state").json()
            print_matches(state)

        elif choice == "7":
            name = input("Player name to delete: ")

            res = requests.delete(
                f"{BASE}/deletePlayer",
                params={"name": name},
            )

            print(res.json())

        elif choice == "0":
            print("Bye!")
            break

        else:
            print("Invalid option")

    except Exception as e:
        print("Error:", e)
import requests

BASE = "http://127.0.0.1:8000"

def draw_board(board):
    def val(x, i): return x if x else str(i)
    print(f"{val(board[0],0)} | {val(board[1],1)} | {val(board[2],2)}")
    print("---------")
    print(f"{val(board[3],3)} | {val(board[4],4)} | {val(board[5],5)}")
    print("---------")
    print(f"{val(board[6],6)} | {val(board[7],7)} | {val(board[8],8)}")


def play_match(match):
    match_id = match["id"]

    while True:
        board = match["board"]
        draw_board(board)

        if match.get("winner"):
            print(f"Winner: {match['winner']}")
            break
        if match.get("is_draw"):
            print("Draw!")
            break

        print(f"Turn: {match['current_player']}")
        pos = input("Choose position (0-8) or q to quit: ")

        if pos == "q":
            break

        try:
            pos = int(pos)
        except:
            print("Invalid input")
            continue

        res = requests.post(f"{BASE}/updateMatch", json={"match_id": match_id, "position": pos})

        if res.status_code != 200:
            print(res.json())
            continue

        match = res.json()
        state = requests.get(f"{BASE}/state").json()
        print_stats(state)

def print_stats(state):
    print("\n=== STATYSTYKI ===")
    print(f"{'Gracz':<15}{'W':<5}{'L':<5}{'D':<5}")
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
        print(f"ID: {m['id']} Players: {m['players']} Winner: {m.get('winner')}")


def menu():
    print("\n=== TIC TAC TOE CLI ===")
    print("1. Create player")
    print("2. Start match")
    print("3. Show stats")
    print("4. Show players")
    print("5. Show matches")
    print("6. Delete player")
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
            p1 = input("Player 1: ")
            p2 = input("Player 2: ")
            res = requests.post(f"{BASE}/startMatch", json=[p1, p2])

            if res.status_code != 200:
                print(res.json())
                continue

            match = res.json()
            print("Match started! Entering game...")
            play_match(match)

        elif choice == "3":
            state = requests.get(f"{BASE}/state").json()
            print_stats(state)

        elif choice == "4":
            state = requests.get(f"{BASE}/state").json()
            print_players(state)

        elif choice == "5":
            state = requests.get(f"{BASE}/state").json()
            print_matches(state)

        elif choice == "6":
            name = input("Player name to delete: ")
            res = requests.delete(f"{BASE}/deletePlayer", params={"name": name})

            print(res.json())

        elif choice == "0":
            print("Bye!")
            break

        else:
            print("Invalid option")

    except Exception as e:
        print("Error:", e)
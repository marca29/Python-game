WIN_PATTERNS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
]

def check_winner(board):
    for a,b,c in WIN_PATTERNS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None

def update_stats(match, result, state):
    for p in match["players"]:
        if p not in state["statistics"]:
            state["statistics"][p] = {"wins": 0, "losses": 0, "draws": 0}

    if result == "draw":
        for p in match["players"]:
            state["statistics"][p]["draws"] += 1
        return

    winner = match["winner"]
    loser = match["players"][0] if match["players"][1] == winner else match["players"][1]

    state["statistics"][winner]["wins"] += 1
    state["statistics"][loser]["losses"] += 1
from fastapi import APIRouter, HTTPException
from models import Player, Move
from state import state_manager
from game import check_winner

router = APIRouter()

@router.post("/createPlayer")
def create_player(player: Player):
    s = state_manager.state
    if player.name in s["players"]:
        raise HTTPException(400, "Exists")
    s["players"].append(player.name)
    s["statistics"][player.name] = {"wins":0,"losses":0,"draws":0}
    state_manager.save()
    return {"ok": True}

@router.post("/startMatch")
def start_match(players: list[str]):
    s = state_manager.state

    if len(players) != 2:
        raise HTTPException(400, "Need 2 players")

    if players[0] == players[1]:
        raise HTTPException(400, "Players must be different")

    for p in players:
        if p not in s["players"]:
            raise HTTPException(404, f"Player {p} not found")

    match_id = len(s["matches"])

    match = {
        "id": match_id,
        "board": [""] * 9,
        "players": players,
        "current_player": players[0],
        "winner": None,
        "is_draw": False
    }

    s["matches"].append(match)
    state_manager.save()
    return match

@router.post("/updateMatch")
def update_match(move: Move):
    s = state_manager.state
    try:
        match = s["matches"][move.match_id]
    except:
        raise HTTPException(404, "Match not found")

    if move.position < 0 or move.position > 8:
        raise HTTPException(400, "Position must be 0-8")

    if match["board"][move.position]:
        raise HTTPException(400, "Invalid move")

    symbol = "X" if match["current_player"] == match["players"][0] else "O"
    match["board"][move.position] = symbol

    result = check_winner(match["board"])

    if result == "draw":
        match["is_draw"] = True
        for p in match["players"]:
            state_manager.state["statistics"][p]["draws"] += 1
    elif result:
        winner = match["current_player"]
        loser = [p for p in match["players"] if p != winner][0]

        match["winner"] = winner

        state_manager.state["statistics"][winner]["wins"] += 1
        state_manager.state["statistics"][loser]["losses"] += 1
    else:
        match["current_player"] = (
            match["players"][1]
            if match["current_player"] == match["players"][0]
            else match["players"][0]
        )

    state_manager.save()
    return match

from fastapi import HTTPException

@router.delete("/deletePlayer")
def delete_player(name: str):
    s = state_manager.state

    if name not in s["players"]:
        raise HTTPException(status_code=404, detail="Player not found")

    for match in s["matches"]:
        if match["winner"] is None and not match["is_draw"]:
            if name in match["players"]:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete player in active match"
                )

    s["players"].remove(name)
    s["statistics"].pop(name, None)
    state_manager.save()

    return {
        "ok": True,
        "deleted_player": name
    }

@router.get("/state")
def get_state():
    return state_manager.state
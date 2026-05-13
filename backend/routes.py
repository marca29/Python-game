from fastapi import APIRouter, HTTPException, Query
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
def start_match(player_name: str = Query(...)):
    s = state_manager.state

    if player_name not in s["players"]:
        raise HTTPException(404, "Player does not exist")

    match = {
        "id": len(s["matches"]),
        "board": ["", "", "", "", "", "", "", "", ""],
        "players": [player_name],
        "current_player": player_name,
        "winner": None,
        "is_draw": False,
        "started": False,
    }

    s["matches"].append(match)
    state_manager.save()

    return match

@router.post("/joinMatch")
def join_match(match_id: int = Query(...), player_name: str = Query(...)):
    s = state_manager.state

    try:
        match = s["matches"][match_id]
    except:
        raise HTTPException(404, "Match not found")

    if player_name not in s["players"]:
        raise HTTPException(404, "Player does not exist")

    if len(match["players"]) >= 2:
        raise HTTPException(400, "Match already full")

    if player_name in match["players"]:
        raise HTTPException(400, "Player already in match")

    match["players"].append(player_name)
    
    match["started"] = True

    state_manager.save()

    return {
        "message": f"{player_name} joined the match",
        "match": match,
    }

@router.post("/updateMatch")
def update_match(move: Move):
    s = state_manager.state

    try:
        match = s["matches"][move.match_id]
    except:
        raise HTTPException(404, "Match not found")

    if match["winner"] or match["is_draw"]:
        raise HTTPException(400, "Match already finished")

    if move.player != match["current_player"]:
        raise HTTPException(400, "Not your turn")

    if move.player not in match["players"]:
        raise HTTPException(400, "Player is not part of this match")

    if move.position < 0 or move.position > 8:
        raise HTTPException(400, "Position must be 0-8")

    if match["board"][move.position]:
        raise HTTPException(400, "Invalid move")

    symbol = "X" if move.player == match["players"][0] else "O"
    match["board"][move.position] = symbol
    result = check_winner(match["board"])

    if result == "draw":
        match["is_draw"] = True

        for p in match["players"]:
            state_manager.state["statistics"][p]["draws"] += 1

    elif result:
        winner = move.player
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

@router.get("/match/{match_id}")
def get_match(match_id: int):
    s = state_manager.state

    try:
        return s["matches"][match_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Match not found")

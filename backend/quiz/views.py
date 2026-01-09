from django.http import JsonResponse
from django.shortcuts import redirect
from inertia import render

from core.helpers import BodyContent, default_props, get_or_none
from quiz.models import Player, PlayerGIF, Session


def index(request, **kwargs):
    """Page to create a new quiz session or join an existing one."""
    page_props = {
        "navbarSize": "small",
    }

    return render(request, "Quiz/LobbyPage", props=default_props(page_props, request, **kwargs))


def join(request, **kwargs):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "method_not_allowed",
        }, status=405)

    post_data = BodyContent(request)

    lobby_code = post_data.get("lobbyCode", "").upper()
    player_name = post_data.get("playerName", "").strip()

    if not lobby_code or len(lobby_code) != 6:
        return JsonResponse({
            "status": "error",
            "message": "invalid_lobby_code",
        }, status=400)

    if not player_name or len(player_name) < 1:
        return JsonResponse({
            "status": "error",
            "message": "invalid_player_name",
        }, status=400)

    # Check if name is valid (Only numbers, letters and whitespaces allowed, max length 50)
    if not all(c.isalnum() or c.isspace() for c in player_name) or len(player_name) > 50:
        return JsonResponse({
            "status": "error",
            "message": "invalid_player_name",
        }, status=400)

    # Check if session exists
    session = get_or_none(Session, id=lobby_code)

    if not session:
        return JsonResponse({
            "status": "error",
            "message": "lobby_not_found",
        }, status=404)

    if session.is_active:
        return JsonResponse({
            "status": "error",
            "message": "lobby_already_started",
        }, status=400)

    if session.players.count() >= session.max_players:
        return JsonResponse({
            "status": "error",
            "message": "lobby_full",
        }, status=400)

    # Check if player name is already taken in this session
    existing_player = Player.objects.filter(session=session, name__iexact=player_name).first()

    if existing_player:
        return JsonResponse({
            "status": "error",
            "message": "name_already_taken",
        }, status=400)

    # Choose a random GIF for the player that is not already taken by other players in the session
    # (If no GIFs are available, the player will have no GIF)
    taken_gif_ids = session.players.filter(gif__isnull=False).values_list('gif_id', flat=True)
    available_gifs = PlayerGIF.objects.exclude(id__in=taken_gif_ids)
    player_gif = available_gifs.order_by('?').first() if available_gifs.exists() else None

    # Create new player
    new_player = Player.objects.create(
        name=player_name,
        gif=player_gif,
        is_host=False,
        session=session,
    )

    return JsonResponse({
        "status": "success",
        "message": "joined_lobby",
        "lobby_code": session.id,
        "player_id": new_player.id,
    })


def lobby(request, lobby_code, **kwargs):
    page_props = {
        "navbarSize": "small",
        "lobbyCode": lobby_code,
    }

    player_id = request.COOKIES.get("quiz_player_id")
    player = get_or_none(Player, id=player_id, session__id=lobby_code) if player_id else None

    if player is None:
        return redirect("quiz:index")

    session = get_or_none(Session, id=lobby_code)

    if session is None:
        return redirect("quiz:index")

    page_props["player"] = player.json()

    return render(request, "Quiz/SessionPage", props=default_props(page_props, request, **kwargs))

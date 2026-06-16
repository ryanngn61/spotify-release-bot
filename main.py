import os
import json
import requests
from datetime import datetime, timedelta
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

spotify = Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
    )
)

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

with open("artists.json", "r", encoding="utf-8") as f:
    artists = json.load(f)

one_week_ago = datetime.now() - timedelta(days=7)
new_releases = []

for artist_name in artists:
    results = spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)

    if not results["artists"]["items"]:
        continue

    artist_id = results["artists"]["items"][0]["id"]

    albums = spotify.artist_albums(
        artist_id,
        album_type="album,single",
        limit=10
    )

    seen = set()

    for album in albums["items"]:
        if album["id"] in seen:
            continue
        seen.add(album["id"])

        release_date = album["release_date"]

        try:
            released = datetime.strptime(release_date, "%Y-%m-%d")
        except:
            try:
                released = datetime.strptime(release_date, "%Y-%m")
            except:
                released = datetime.strptime(release_date, "%Y")

        if released >= one_week_ago:
            new_releases.append(
                f"• **{artist_name}** — {album['name']}"
            )

message = "# 🎵 Weekly Music Update\n\n"

if new_releases:
    message += "\n".join(new_releases)
else:
    message += "No new releases this week."

requests.post(
    WEBHOOK_URL,
    json={"content": message}
)

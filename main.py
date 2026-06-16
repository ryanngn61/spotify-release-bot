```python
import os
import json
import requests
from datetime import datetime, timedelta
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify authentication
spotify = Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
    )
)

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# Load artists
with open("artists.json", "r", encoding="utf-8") as f:
    artists = json.load(f)

# Check releases from the last 14 days
cutoff_date = datetime.now() - timedelta(days=14)

new_releases = []
seen_albums = set()

for artist_name in artists:
    try:
        results = spotify.search(
            q=f"artist:{artist_name}",
            type="artist",
            limit=1
        )

        if not results["artists"]["items"]:
            continue

        artist = results["artists"]["items"][0]
        artist_id = artist["id"]

        albums = spotify.artist_albums(
            artist_id,
            album_type="album,single",
            limit=20
        )

        for album in albums["items"]:

            # Skip duplicates
            if album["id"] in seen_albums:
                continue

            seen_albums.add(album["id"])

            release_date = album["release_date"]

            try:
                released = datetime.strptime(release_date, "%Y-%m-%d")
            except:
                try:
                    released = datetime.strptime(release_date, "%Y-%m")
                except:
                    released = datetime.strptime(release_date, "%Y")

            if released >= cutoff_date:

                image_url = None
                if album["images"]:
                    image_url = album["images"][0]["url"]

                new_releases.append({
                    "artist": artist_name,
                    "album": album["name"],
                    "date": release_date,
                    "image": image_url
                })

    except Exception as e:
        print(f"Error with {artist_name}: {e}")

# Sort newest first
new_releases.sort(key=lambda x: x["date"], reverse=True)

# Nothing found
if not new_releases:
    requests.post(
        WEBHOOK_URL,
        json={
            "content": "🎵 No new releases in the last 14 days."
        }
    )

# Send embeds
else:
    for release in new_releases:

        embed = {
            "title": release["album"],
            "description":
                f"**Artist:** {release['artist']}\n"
                f"**Released:** {release['date']}",
            "color": 5763719
        }

        if release["image"]:
            embed["image"] = {
                "url": release["image"]
            }

        requests.post(
            WEBHOOK_URL,
            json={
                "embeds": [embed]
            }
        )
```

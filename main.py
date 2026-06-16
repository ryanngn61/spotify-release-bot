```python
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

cutoff_date = datetime.now() - timedelta(days=14)

new_releases = []
seen_albums = set()

for artist_name in artists:

    try:
        print(f"Checking {artist_name}...")

        results = spotify.search(
            q=f"artist:{artist_name}",
            type="artist",
            limit=1
        )

        if not results["artists"]["items"]:
            print(f"Couldn't find {artist_name}")
            continue

        artist = results["artists"]["items"][0]
        artist_id = artist["id"]

        albums = spotify.artist_albums(
            artist_id,
            album_type="album,single",
            limit=50
        )

        for album in albums["items"]:

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
                if len(album["images"]) > 0:
                    image_url = album["images"][0]["url"]

                new_releases.append({
                    "artist": artist_name,
                    "album": album["name"],
                    "date": release_date,
                    "image": image_url
                })

    except Exception as e:
        print(f"Skipping {artist_name}: {e}")

# newest first
new_releases.sort(key=lambda x: x["date"], reverse=True)

if not new_releases:

    requests.post(
        WEBHOOK_URL,
        json={"content": "🎵 No new releases in the last 14 days."}
    )

else:

    description = ""

    for release in new_releases:
        description += (
            f"• **{release['artist']}** — {release['album']}\n"
            f"Released: {release['date']}\n\n"
        )

    embed = {
        "title": "🎵 Weekly Music Update",
        "description": description,
        "color": 5763719
    }

    # Use the first release's artwork as the big image
    if new_releases[0]["image"]:
        embed["thumbnail"] = {
            "url": new_releases[0]["image"]
        }

    requests.post(
        WEBHOOK_URL,
        json={
            "embeds": [embed]
        }
    )

print("Done!")
```

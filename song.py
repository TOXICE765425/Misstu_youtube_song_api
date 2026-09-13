import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Misstu YouTube Song API is running",
        "usage": "/api/song?query=Tum%20Hi%20Ho",
        "powered_by": "Toxice Hacker",
        "developer": "@misstu001"
    })


@app.route("/api/song")
def song_search():

    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "error": "query is required",
            "example": "/api/song?query=Tum%20Hi%20Ho",
            "powered_by": "Toxice Hacker",
            "developer": "@misstu001"
        }), 400

    if not YOUTUBE_API_KEY:
        return jsonify({
            "success": False,
            "error": "YOUTUBE_API_KEY is not configured",
            "powered_by": "Toxice Hacker",
            "developer": "@misstu001"
        }), 500

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "order": "relevance",
        "regionCode": "IN",
        "key": YOUTUBE_API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": data.get("error", {}).get(
                    "message",
                    "YouTube API request failed"
                ),
                "powered_by": "Toxice Hacker",
                "developer": "@misstu001"
            }), response.status_code

        results = []

        for item in data.get("items", []):

            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            snippet = item.get("snippet", {})

            results.append({
                "video_id": video_id,
                "title": snippet.get("title"),
                "artist": snippet.get("channelTitle"),
                "channel": snippet.get("channelTitle"),
                "description": snippet.get("description"),
                "published_at": snippet.get("publishedAt"),
                "thumbnail": (
                    snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                ),
                "youtube_url":
                    f"https://www.youtube.com/watch?v={video_id}"
            })

        return jsonify({
            "success": True,
            "query": query,
            "count": len(results),
            "results": results,
            "powered_by": "Toxice Hacker",
            "developer": "@misstu001"
        })

    except requests.exceptions.Timeout:

        return jsonify({
            "success": False,
            "error": "YouTube API timeout",
            "powered_by": "Toxice Hacker",
            "developer": "@misstu001"
        }), 504

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e),
            "powered_by": "Toxice Hacker",
            "developer": "@misstu001"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )

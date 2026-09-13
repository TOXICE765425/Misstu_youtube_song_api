from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import urllib.request
import urllib.parse


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/song":
            self.send_json(404, {
                "success": False,
                "error": "Use /api/song?query=Song%20Name"
            })
            return

        query = parse_qs(parsed.query).get("query", [""])[0].strip()

        if not query:
            self.send_json(400, {
                "success": False,
                "error": "query is required"
            })
            return

        api_key = os.environ.get("YOUTUBE_API_KEY")

        if not api_key:
            self.send_json(500, {
                "success": False,
                "error": "YOUTUBE_API_KEY is not configured"
            })
            return

        params = urllib.parse.urlencode({
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 10,
            "order": "relevance",
            "regionCode": "IN",
            "key": api_key
        })

        url = "https://www.googleapis.com/youtube/v3/search?" + params

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))

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
                    "thumbnail": (
                        snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url")
                    ),
                    "youtube_url":
                        f"https://www.youtube.com/watch?v={video_id}"
                })

            self.send_json(200, {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results,
                "powered_by": "Toxice Hacker",
                "developer": "@misstu001"
            })

        except Exception as e:
            self.send_json(500, {
                "success": False,
                "error": str(e),
                "powered_by": "Toxice Hacker",
                "developer": "@misstu001"
            })

    def send_json(self, status, data):
        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.end_headers()
        self.wfile.write(body)

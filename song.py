from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import html
import os


# ==========================================
# MISSTU SONG SEARCH API
# ==========================================

API_NAME = "Misstu Song Search API"
API_VERSION = "1.0.0"
POWERED_BY = "Toxice Hacker"
DEVELOPER = "@misstu001"


def send_json(handler, status_code, data):

    body = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    handler.send_response(status_code)

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "GET, OPTIONS"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "*"
    )

    handler.send_header(
        "Content-Length",
        str(len(body))
    )

    handler.end_headers()

    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):

    # ==========================================
    # OPTIONS / CORS
    # ==========================================

    def do_OPTIONS(self):

        send_json(
            self,
            200,
            {
                "success": True,
                "powered_by": POWERED_BY,
                "developer": DEVELOPER
            }
        )


    # ==========================================
    # GET
    # ==========================================

    def do_GET(self):

        parsed = urlparse(self.path)

        path = parsed.path

        params = parse_qs(parsed.query)


        # ======================================
        # HOME
        # ======================================

        if path == "/" or path == "":

            send_json(
                self,
                200,
                {
                    "success": True,
                    "name": API_NAME,
                    "version": API_VERSION,

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER,

                    "usage":
                        "/api/song?query=Tum%20Hi%20Ho"
                }
            )

            return


        # ======================================
        # SONG SEARCH
        # ======================================

        if path != "/api/song":

            send_json(
                self,
                404,
                {
                    "success": False,
                    "error": "Endpoint not found",

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        # ======================================
        # QUERY
        # ======================================

        query = params.get(
            "query",
            [""]
        )[0].strip()


        if not query:

            send_json(
                self,
                400,
                {
                    "success": False,

                    "error":
                        "query parameter is required",

                    "example":
                        "/api/song?query=Tum%20Hi%20Ho",

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        # ======================================
        # API KEY
        # ======================================

        API_KEY = os.environ.get(
            "YOUTUBE_API_KEY"
        )


        if not API_KEY:

            send_json(
                self,
                500,
                {
                    "success": False,

                    "error":
                        "YOUTUBE_API_KEY is not configured",

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        # ======================================
        # YOUTUBE API URL
        # ======================================

        youtube_url = (
            "https://www.googleapis.com/youtube/v3/search"
            "?part=snippet"
            "&q=" + quote(query)
            "&type=video"
            "&maxResults=10"
            "&order=relevance"
            "&regionCode=IN"
            "&key=" + quote(API_KEY)
        )


        # ======================================
        # REQUEST YOUTUBE
        # ======================================

        try:

            request = Request(
                youtube_url,
                headers={
                    "User-Agent":
                        "Mozilla/5.0"
                }
            )


            with urlopen(
                request,
                timeout=15
            ) as result:

                youtube_data = json.loads(
                    result.read().decode(
                        "utf-8"
                    )
                )


        except HTTPError as error:

            try:

                error_data = json.loads(
                    error.read().decode(
                        "utf-8"
                    )
                )

            except Exception:

                error_data = {
                    "message": str(error)
                }


            send_json(
                self,
                error.code,
                {
                    "success": False,
                    "query": query,

                    "error": error_data,

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        except URLError as error:

            send_json(
                self,
                502,
                {
                    "success": False,
                    "query": query,

                    "error":
                        "YouTube connection failed",

                    "details": str(error),

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        except Exception as error:

            send_json(
                self,
                500,
                {
                    "success": False,
                    "query": query,

                    "error": str(error),

                    "powered_by": POWERED_BY,
                    "developer": DEVELOPER
                }
            )

            return


        # ======================================
        # FORMAT RESULTS
        # ======================================

        results = []


        for item in youtube_data.get(
            "items",
            []
        ):

            video_id = item.get(
                "id",
                {}
            ).get(
                "videoId"
            )


            if not video_id:
                continue


            snippet = item.get(
                "snippet",
                {}
            )


            title = html.unescape(
                snippet.get(
                    "title",
                    ""
                )
            )


            description = html.unescape(
                snippet.get(
                    "description",
                    ""
                )
            )


            thumbnails = snippet.get(
                "thumbnails",
                {}
            )


            thumbnail = (

                thumbnails.get(
                    "high",
                    {}
                ).get(
                    "url"
                )

                or

                thumbnails.get(
                    "medium",
                    {}
                ).get(
                    "url"
                )

                or

                thumbnails.get(
                    "default",
                    {}
                ).get(
                    "url"
                )
            )


            results.append(
                {
                    "video_id": video_id,

                    "title": title,

                    "artist":
                        snippet.get(
                            "channelTitle"
                        ),

                    "channel":
                        snippet.get(
                            "channelTitle"
                        ),

                    "description":
                        description,

                    "published_at":
                        snippet.get(
                            "publishedAt"
                        ),

                    "thumbnail":
                        thumbnail,

                    "youtube_url":
                        "https://www.youtube.com/watch?v="
                        + video_id
                }
            )


        # ======================================
        # FINAL RESPONSE
        # ======================================

        send_json(
            self,
            200,
            {
                "success": True,

                "query": query,

                "count":
                    len(results),

                "results":
                    results,

                "powered_by":
                    POWERED_BY,

                "developer":
                    DEVELOPER
            }
        )
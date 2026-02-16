from fastapi.responses import JSONResponse, Response


def build_response(r):
    content_type = r.headers.get("content-type", "")

    if "application/json" in content_type:
        return JSONResponse(
            content=r.json(),
            status_code=r.status_code
        )

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=content_type
    )

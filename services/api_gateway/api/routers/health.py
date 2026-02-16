from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
async def health():
    return {"status": "ok"}

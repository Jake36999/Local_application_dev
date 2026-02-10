from fastapi import APIRouter, Body


import uuid

class GlobalSessionState:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.active_lens = None
        self.dialectical_mode = False

session_state = GlobalSessionState()
router = APIRouter()

@router.post("/system/set-cognitive-state")
async def set_cognitive_state(
    lens: str = Body(..., embed=True),
    dialectical: bool = Body(..., embed=True)
):
    session_state.active_lens = lens
    session_state.dialectical_mode = dialectical
    return {"status": "updated", "lens": lens, "dialectical": dialectical}

@router.get("/system/cognitive-state")
async def get_cognitive_state():
    return {
        "lens": session_state.active_lens,
        "dialectical": session_state.dialectical_mode
    }

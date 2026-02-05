from fastapi import APIRouter, Body

class GlobalSessionState:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalSessionState, cls).__new__(cls)
            cls._instance.active_lens = "None"
            cls._instance.dialectical_mode = False
        return cls._instance

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

import secrets
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

EMAIL = "23f3003379@ds.study.iitm.ac.in"
API_KEY = "ak_sweo81b4shpg6b7ns1f9uasm"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],   # lets the browser send the custom X-API-Key header
)


@app.get("/")
def health():
    return {"status": "ok"}


def unauthorized():
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})


@app.post("/analytics")
async def analytics(request: Request):
    # 1) Auth first, before touching the body
    key = request.headers.get("x-api-key")
    if key is None or not secrets.compare_digest(key.encode(), API_KEY.encode()):
        return unauthorized()

    # 2) Parse the body
    try:
        body = await request.json()
        events = body["events"]
        if not isinstance(events, list):
            raise ValueError
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid body"})

    # 3) Aggregate
    users = set()
    revenue = 0.0
    per_user = defaultdict(float)   # positive-amount totals only

    for e in events:
        user = e.get("user")
        amount = float(e.get("amount", 0) or 0)
        users.add(user)
        if amount > 0:
            revenue += amount
            per_user[user] += amount

    top_user = max(per_user, key=per_user.get) if per_user else None

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": revenue,
        "top_user": top_user,
    }

from fastapi import FastAPI, Request
from service import EventService

app = FastAPI()

@app.post("/events")
async def post_event(event: dict):
    EventService.save_event(event)
    return {"status": "ok"}

@app.get("/events")
def get_events():
    return {"events": []}

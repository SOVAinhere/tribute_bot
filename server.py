from fastapi import FastAPI, Request
from db import activate_plan

app = FastAPI()


@app.post("/webhook/tribute")
async def tribute_webhook(request: Request):
    data = await request.json()
    print("Webhook data:", data)

    user_id = data.get("user_id")
    plan = data.get("plan")

    if user_id and plan:
        await activate_plan(user_id, plan)

    return {"ok": True}

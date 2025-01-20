from fastapi import FastAPI
from app.api.auth import router as AuthRouter
app = FastAPI()


app.include_router(AuthRouter)
@app.get("/")
async def root():
    return {"message": "Hello World"}

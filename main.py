from fastapi import FastAPI

from api.routing import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return "Server is running."

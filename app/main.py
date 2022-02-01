from fastapi import FastAPI
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware
# from app import models
# from app.database import engine

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "https://www.google.com"
]

# allows CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "I'm root."}

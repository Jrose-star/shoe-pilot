from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, kb, summarize, auth
from app.database import init_db

app = FastAPI(title="ShoePilot API")
# 2. 启动时自动建表
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在这里注册路由
app.include_router(chat.router)
app.include_router(kb.router)
app.include_router(summarize.router)
app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "ShoePilot 后端运行正常"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

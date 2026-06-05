# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from config import settings
from agent.graph import create_agent
from api.routes import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Setup the checkpointer
    async with AsyncPostgresSaver.from_conn_string(settings.db_url) as checkpointer:
        await checkpointer.setup()
        
        # 2. Store the compiled agent in the main app state
        app.state.agent = await create_agent(checkpointer)
        yield

# 3. Create the main app and pass the lifespan handler
app = FastAPI(lifespan=lifespan)

# 4. Include the router
app.include_router(chat_router)

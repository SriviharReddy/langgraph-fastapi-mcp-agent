from fastapi import APIRouter, Request
from uuid import uuid4
from .schema import ChatRequest
from utilities.logging import setup_logging
import logging
from typing import AsyncIterator
import json
from langgraph.graph.state import CompiledStateGraph
from sse_starlette.sse import EventSourceResponse

setup_logging()
logger = logging.getLogger("api.routes")

router = APIRouter(prefix="/chat")


async def stream_chat(
    request: Request,
    message: str,
    thread_id: str,
) -> AsyncIterator[dict]:

    graph: CompiledStateGraph = request.app.state.agent
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    inputs = {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ]
    }

    yield {
        "event": "meta",
        "data": json.dumps(
            {
                "thread_id": thread_id,
            }
        ),
    }

    try:
        async for event in graph.astream_events(
            inputs,
            config=config,
            version="v2",
        ):
            if await request.is_disconnected():
                logger.info("Client disconnected (thread=%s)", thread_id)
                break

            match event["event"]:
                case "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if not chunk:
                        continue
                    text = chunk.content
                    if text:
                        yield {
                            "data": json.dumps(
                                {
                                    "event": "token",
                                    "content": text,
                                }
                            ),
                        }

                case "on_tool_start":
                    yield {
                        "data": json.dumps(
                            {
                                "event": "tool_start",
                                "tool": event.get("name"),
                            }
                        ),
                    }

                case "on_tool_end":
                    yield {
                        "data": json.dumps(
                            {
                                "event": "tool_end",
                                "tool": event.get("name"),
                            }
                        ),
                    }

                case _:
                    continue

        yield {
            "data": json.dumps(
                {
                    "event": "done",
                    "thread_id": thread_id,
                }
            ),
        }

    except Exception as exc:
        logger.exception(
            "Chat stream failed (thread=%s)",
            thread_id,
        )
        yield {
            "data": json.dumps(
                {
                    "event": "error",
                    "type": exc.__class__.__name__,
                    "detail": str(exc),
                }
            ),
        }


@router.post("")
async def chat(
    request: Request,
    body: ChatRequest,
):
    thread_id = body.thread_id or str(uuid4())
    return EventSourceResponse(
        stream_chat(
            request=request,
            message=body.message,
            thread_id=thread_id,
        ),
        ping=15,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

llm = init_chat_model("")


async def chat_node(state: MessagesState):

    message = state["messages"][-1]
    result = llm.ainvoke(message)

    return {"messages": [result]}


checkpoint = MemorySaver()

graph = StateGraph(MessagesState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

workflow = graph.compile(checkpointer=checkpoint)

import os
import time
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash", 
    api_key="Google Gemini API" # Replace with your actual key
)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def get_text(msg_content):
    if isinstance(msg_content, str):
        return msg_content
    if isinstance(msg_content, list):
        text_accumulator = []
        for item in msg_content:
            if isinstance(item, str):
                text_accumulator.append(item)
            elif isinstance(item, dict):
                text_accumulator.append(item.get("text", ""))
            else:
                text_accumulator.append(str(item))
        return "".join(text_accumulator)
    if hasattr(msg_content, "content"):
        return get_text(msg_content.content)
    return str(msg_content)

def researcher_node(state: AgentState):
    print("\n[NODE: Researcher] Gathering historical facts...")
    time.sleep(3)
    messages_to_send = [SystemMessage(content=RESEARCHER_PROMPT)] + state["messages"]
    response = llm.invoke(messages_to_send)
    return {"messages": [response]}

def scriptwriter_node(state: AgentState):
    print("\n[NODE: Scriptwriter] Drafting the Roblox R6 vertical script...")
    # Force the LLM to act as the Scriptwriter
    messages_to_send = [SystemMessage(content=SCRIPTWRITER_PROMPT)] + state["messages"]
    response = llm.invoke(messages_to_send)
    return {"messages": [response]}

def routing_logic(state: AgentState):
    last_message = get_text(state["messages"][-1].content)
    
    if "NEED_RESEARCH" in last_message:
        print("-> ROUTER: Scriptwriter needs more context. Looping back to Researcher.")
        return "researcher"
        
    print("-> ROUTER: Script is complete. Ending graph.")
    return END


workflow = StateGraph(AgentState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("scriptwriter", scriptwriter_node)

workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "scriptwriter")

workflow.add_conditional_edges(
    "scriptwriter",
    routing_logic,
    {"researcher": "researcher", END: END}
)

app_graph = workflow.compile()

if __name__ == "__main__":
    initial_input = {"messages": [HumanMessage(content="Create a video script about the Mahabalipuram temple.")]}
    print("Starting Multi-Agent Workflow...")
    
    for event in app_graph.stream(initial_input, config={"recursion_limit": 10}):
        for key, value in event.items():
            print(f"\n--- Output from {key.upper()} ---")
            print(get_text(value['messages'][-1].content))
            print("-----------------------------------")

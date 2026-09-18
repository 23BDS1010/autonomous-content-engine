from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from multiagent import app_graph
# Import your compiled graph from your agent file (e.g., agent.py)
# from agent import app as compiled_graph 

app = FastAPI(
    title="Autonomous Content Engine API",
    description="Multi-Agent RAG Pipeline for Mahabalipuram Content Generation",
    version="1.0.0"
)
class GenerationRequest(BaseModel):
    topic: str
    target_aesthetic: str = "Roblox R6 style"
class GenerationResponse(BaseModel):
    status: str
    topic: str
    script: str

@app.post("/generate-script", response_model=GenerationResponse)
async def generate_script(request: GenerationRequest):
    try:
        # Initial state payload for your LangGraph application
        initial_state = {
            "messages": [("user", f"Generate a video script about {request.topic}")],
            "target_aesthetic": request.target_aesthetic,
            "target_layout": "9:16 vertical"
        }
	# Execute the compiled LangGraph workflow
        result = app_graph.invoke(initial_state)
        
        # Extract the final output message safely
        final_message = result["messages"][-1].content if hasattr(result["messages"][-1],"content") else str(result["messages"][-1])
                
        # Placeholder response for structure demonstration
        return {
            "status": "success",
            "topic": request.topic,
            "script": final_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.chat import answer_query

app = FastAPI(title="ECI Chatbot API")

# Add CORS so Next.js frontend can communicate with it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a local dev tool, permit all for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    """Answers queries via the Chat Agent and Graph-RAG pipeline."""
    response_text = answer_query(request.query)
    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

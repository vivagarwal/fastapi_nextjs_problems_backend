from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fastapi-nextjs-problems-frontend.vercel.app","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputRequest(BaseModel):
    inp: str

def is_palindrome(y: str) -> bool:
    x = int(y)
    if x < 0 or (x > 0 and x % 10 == 0):
        return False
    sum = 0
    while x > sum:
        sum = (sum * 10) + x % 10
        x = x // 10
    return (sum // 10 == x or sum == x)

@app.get("/")
async def root():
    return {"message": "Welcome to root page!"}

@app.get("/api/hello")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.post("/api/check-palindrome")
async def check_palindrome(request: InputRequest):
    inp1 = request.inp
    result = is_palindrome(inp1)
    return {"input":inp1,"output": result}



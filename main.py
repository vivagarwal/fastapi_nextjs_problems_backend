from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from data_problems import problems_list
import importlib

app = FastAPI()

# Define the path to the HTML file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "templates", "problem_description_0.html")

# Import the solutions module
sol_module = importlib.import_module("solution")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fastapi-nextjs-problems-frontend.vercel.app","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputRequest(BaseModel):
    inp: str

def get_html_file_path(id : int) -> str:
    s = "problem_description_"+str(id)+".html"
    HTML_FILE_PATH = os.path.join(BASE_DIR, "templates", s)
    return HTML_FILE_PATH

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

# @app.get("/api/get-problem-description")
# async def get_problem_description():
#     # Return the HTML file as a FileResponse
#     return FileResponse(HTML_FILE_PATH, media_type='text/html')

@app.get("/api/get-problem-description/{id}")
async def get_problem_description(id: int):
    #return {"id":id}
    path = get_html_file_path(id)
    # Return the HTML file as a FileResponse
    return FileResponse(path, media_type='text/html')

@app.post("/api/check-palindrome")
async def check_palindrome(request: InputRequest):
    inp1 = request.inp
    result = is_palindrome(inp1)
    return {"input":inp1,"output": result}

@app.post("/api/check-solution/{id}")
async def check_solution(id: int, request: InputRequest):
    inp1 = request.inp
    filtered_list = [d for d in problems_list if d.get('id') == id]
    solution_func_name = filtered_list[0].get('solution_func')
    # return {solution_func_name}
    solution_func = getattr(sol_module, solution_func_name, None)
    result = solution_func(inp1)
    return {"input":inp1,"output": result}

@app.get("/api/get-all-problems")
async def get_all_problems():
    return {"problems": problems_list}




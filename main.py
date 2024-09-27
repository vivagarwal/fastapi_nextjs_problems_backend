from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from data_problems import problems_list
import importlib
import asyncio
import subprocess
import uuid
import tempfile



app = FastAPI()

# Define the path to the HTML file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#HTML_FILE_PATH = os.path.join(BASE_DIR, "templates", "problem_description_0.html")

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

class RunRequest(BaseModel):
    language:str='cpp'
    code:str
    input:Optional[str]= ''

def get_html_file_path(id : int) -> str:
    s = "problem_description_"+str(id)+".html"
    HTML_FILE_PATH = os.path.join(BASE_DIR, "templates", s)
    return HTML_FILE_PATH

async def generate_file(language, code, input):
    file_extension = {'cpp': 'cpp', 'java': 'java', 'py': 'py', 'c': 'c'}
    filename = f"{str(uuid.uuid4())}.{file_extension[language]}"
    input_filename = f"{str(uuid.uuid4())}.txt"
    with open(filename, 'w') as file:
        file.write(code)
    with open(input_filename, 'w') as file:
        file.write(input)
    return filename, input_filename

async def execute_cpp(file_path, input_path):
    # Get the directory of the source file
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # Create a temporary directory for compilation and execution
    with tempfile.TemporaryDirectory() as temp_dir:
        if os.name == 'nt':  # Windows
            compiled_path = os.path.join(temp_dir, f"{file_name_without_ext}.exe")
            compile_command = f"g++ \"{file_path}\" -o \"{compiled_path}\""
            run_command = f"\"{compiled_path}\" < \"{input_path}\""
        else:  # macOS/Linux
            compiled_path = os.path.join(temp_dir, file_name_without_ext)
            compile_command = f"g++ \"{file_path}\" -o \"{compiled_path}\""
            run_command = f"chmod +x \"{compiled_path}\" && \"{compiled_path}\" < \"{input_path}\""

        try:
            # Compile
            compile_process = await asyncio.create_subprocess_shell(
                compile_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, compile_stderr = await compile_process.communicate()

            if compile_process.returncode != 0:
                return {'output': f"Compilation error: {compile_stderr.decode()}"}

            # Run
            run_process = await asyncio.create_subprocess_shell(
                run_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await run_process.communicate()

            if stderr:
                return {'output': stderr.decode()}
            return {'output': stdout.decode()}
        except Exception as e:
            return {'output': f"Execution error: {str(e)}"}


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

@app.post("/run")
async def run_code(request: RunRequest):
    try:
        file_path, input_path = await generate_file(request.language, request.code, request.input)
        result = None

        if(request.language == 'cpp'):
            result=await execute_cpp(file_path,input_path)
        return {"output":result['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




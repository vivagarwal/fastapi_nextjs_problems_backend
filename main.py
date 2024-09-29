import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
import os
from data_problems import problems_list
import importlib
import asyncio
import subprocess
import uuid
import tempfile
from dotenv import load_dotenv
from typing import List


load_dotenv()

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

class SubmitRequest(BaseModel):
    id: int
    language: str = 'cpp'
    code: str

class TestResult(BaseModel):
    input: str
    expectedOutput: str
    actualOutput: str
    passed: bool

class SubmitResponse(BaseModel):
    success: bool
    status: str
    message: str

def get_html_file_path(id : int) -> str:
    s = "problem_description_"+str(id)+".html"
    HTML_FILE_PATH = os.path.join(BASE_DIR, "templates", s)
    return HTML_FILE_PATH

def generate_file(language, code, input):
    file_extension = {'cpp': 'cpp', 'java': 'java', 'py': 'py', 'c': 'c'}
    temp_dir = os.getenv('OUTPUT_TEMP_DIR')
    os.makedirs(temp_dir, exist_ok=True)
    filename = os.path.join(temp_dir,f"{str(uuid.uuid4())}.{file_extension[language]}")
    input_filename = os.path.join(temp_dir,f"{str(uuid.uuid4())}.txt")
    with open(filename, 'w') as file:
        file.write(code)
    with open(input_filename, 'w') as file:
        file.write(input)
    return filename, input_filename

def cleanup_files(file_path, input_path):
    files_to_delete = [file_path, input_path]
    
    for file in files_to_delete:
        try:
            os.remove(file)
            print(f"Successfully deleted {file}")
        except OSError as e:
            print(f"Error deleting {file}: {e.strerror}")

def execute_cpp(file_path, input_path):
    # Get the directory of the source file
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # Create a temporary directory for compilation and execution
    #with os.getenv('OUTPUT_TEMP_DIR') as temp_dir:
    temp_dir = os.getenv('OUTPUT_TEMP_DIR')

    if os.name == 'nt':  # Windows
        compiled_path = os.path.join(temp_dir, f"{file_name_without_ext}.exe")
        compile_command = f"g++ \"{file_path}\" -o \"{compiled_path}\""
        run_command = f"\"{compiled_path}\" < \"{input_path}\""
    else:  # macOS/Linux
        compiled_path = os.path.join(temp_dir, f"{file_name_without_ext}.out")
        compile_command = f"g++ \"{file_path}\" -o \"{compiled_path}\""
        run_command = f"chmod +x \"{compiled_path}\" && \"{compiled_path}\" < \"{input_path}\""

    # try:
    #     # Compile
    #     compile_process = await asyncio.create_subprocess_shell(
    #         compile_command,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE
    #     )
    #     _, compile_stderr = await compile_process.communicate()

    #     if compile_process.returncode != 0:
    #         return {'output': f"Compilation error: {compile_stderr.decode()}"}

    #     # Run
    #     run_process = await asyncio.create_subprocess_shell(
    #         run_command,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE
    #     )
    #     stdout, stderr = await run_process.communicate()

    #     if stderr:
    #         return {'output': stderr.decode()}
    #     return {'output': stdout.decode()}
    # except Exception as e:
    #     return {'output': f"Execution error: {str(e)}"}
    os.system(compile_command)
    output = os.popen(run_command).read()
    #os.remove(compiled_path)
    cleanup_files(file_path, input_path)
    # Also remove the compiled file if it exists
    if os.path.exists(compiled_path):
        os.remove(compiled_path)
    return {'output': output}

def execute_python(file_path, input_path):
    # Get the Python interpreter path
    if os.name == 'nt':
        python_command = "python"
    else:
        python_command = "python3"

    # Construct the command to run the Python script with input
    command = f'{python_command} "{file_path}" < "{input_path}"'

    try:
        # Execute the command and capture the output
        output = os.popen(command).read()
        return {'output': output}
    except Exception as e:
        return {'output': f"Execution error: {str(e)}"}
    finally:
        # Clean up the files
        cleanup_files(file_path, input_path)

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

# @app.post("/api/check-palindrome")
# async def check_palindrome(request: InputRequest):
#     inp1 = request.inp
#     result = is_palindrome(inp1)
#     return {"input":inp1,"output": result}

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

@app.post("/api/run")
async def run_code(request: RunRequest):
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Empty code!")
        file_path, input_path = generate_file(request.language, request.code, request.input)
        result = None

        if request.language == 'cpp':
                result = execute_cpp(file_path, input_path)
        elif request.language == 'py':
                result = execute_python(file_path, input_path)
        elif request.language not in ['cpp', 'py']:
                raise HTTPException(status_code=400, detail="Unsupported language")

        return {"output":result['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit", response_model=SubmitResponse)
async def submit_solution(request: SubmitRequest):
    if not request.code:
        raise HTTPException(status_code=400, detail="Empty code!")

    try:
        # Get the problem details based on the ID
        problem = next((p for p in problems_list if p['id'] == request.id), None)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        test_cases = problem.get('test_cases', [])
        if not test_cases:
            raise HTTPException(status_code=400, detail="No test cases found for this problem")

        results = []
        passed_count = 0
        total_count = len(test_cases)

        for test_case in test_cases:
            file_path, input_path = generate_file(request.language, request.code, test_case['input'])
            
            if request.language == 'cpp':
                result = execute_cpp(file_path, input_path)
            elif request.language == 'py':
                result = execute_python(file_path, input_path)
            elif request.language not in ['cpp', 'py']:
                raise HTTPException(status_code=400, detail="Unsupported language")

            actual_output = result['output'].strip()
            expected_output = str(test_case['output']).strip()
            passed = actual_output == expected_output

            if passed:
                passed_count += 1

            results.append(TestResult(
                input=test_case['input'],
                expectedOutput=expected_output,
                actualOutput=actual_output,
                passed=passed
            ))

        all_passed = passed_count == total_count
        
        return SubmitResponse(
            success=True,
            results=results,
            status="Success" if all_passed else "Failed",
            message=f"Passed {passed_count}/{total_count} test cases",
            passed_count=passed_count,
            total_count=total_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



to run FAST API server locally:

```
python -m venv .venv
.venv\Scripts\activate (windows) or source .venv/bin/activate(linux)
pip install -r requirements.txt
uvicorn main:app --reload
```
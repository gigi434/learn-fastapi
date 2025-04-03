"# Fastapi-The-Complete-Course"

Course and code created by: Eric Roby

### FastAPIを起動する場合

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port=8000 --host=0.0.0.0
```

#### Project4から
何らかのコードでつまずいた場合、start/endディレクトリではなくUdemy講座のコース番号を示している
```bash
cd /home/vscode/workspace/Project 4/end/TodoApp
pip install -r requirements.txt
cd ../
uvicorn TodoApp.main:app --reload --port=8000 --host=0.0.0.0
```
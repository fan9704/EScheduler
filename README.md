# FastAPI Template

---

## Requirements

1. uv - package manager 
2. Python 3.12+ - programming language
3. Docker - containerization platform
4. Docker Compose - tool for defining and running multi-container Docker applications

### UV Install

#### Windows 

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "{HOME_DIRE}\.local\bin;$env:Path"
```

#### Linux/MacOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

----

## Getting Started

### Clone the repository

```bash
git clone https://github.com/fan9704/fastapi-template.git
```

### Navigate to the project directory

```bash
cd fastapi-template
```

### Install dependencies

```bash
uv sync
```

### Lock dependencies

```bash
uv lock
``` 

### Create a `.env` file in the root directory and add your environment variables

```shell
# Paste the .env.example content into the .env file
```

### Create related service from docker-compose

```bash
docker-compose up -d
```

### Run the application

```bash
uv run python main.py
```

import uvicorn
from src.configs import APPLICATION_PORT

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=APPLICATION_PORT, reload=True)

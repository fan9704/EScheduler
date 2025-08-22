from fastapi import HTTPException
from starlette import status

class NotAuthenticated(HTTPException):
    def __init__(self, detail: str = "User not authenticated") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})

class CredentialsDataWrong(NotAuthenticated):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(detail=detail)
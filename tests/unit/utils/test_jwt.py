from datetime import datetime, timezone

import pytest
from jose import jwt

from src import exceptions
from src.utils import jwt as jwt_utils


# -----------------------
# jwt_encode_content
# -----------------------
def test_jwt_encode_content_returns_string():
    data = {"sub": "123"}
    token = jwt_utils.jwt_encode_content(data)
    assert isinstance(token, str)


# -----------------------
# create_access_token
# -----------------------
def test_create_access_token_sets_exp():
    data = {"sub": "user1"}
    token = jwt_utils.create_access_token(data, expires_delta=5)
    payload = jwt.decode(token, jwt_utils.SECRET_KEY, algorithms=[jwt_utils.ALGORITHM])
    assert payload["sub"] == "user1"
    # exp timestamp 應該晚於當前時間
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


# -----------------------
# decode_jwt
# -----------------------
@pytest.mark.asyncio
async def test_decode_jwt_success():
    token = jwt_utils.jwt_encode_content({"sub": "123"})

    # 模擬 Depends
    async def fake_oauth2_scheme():
        return token

    result = await jwt_utils.decode_jwt(token=await fake_oauth2_scheme())
    assert result["sub"] == "123"


@pytest.mark.asyncio
async def test_decode_jwt_no_sub_raises():
    token = jwt_utils.jwt_encode_content({"foo": "bar"})

    async def fake_oauth2_scheme():
        return token

    with pytest.raises(exceptions.CredentialsDataWrong):
        await jwt_utils.decode_jwt(token=await fake_oauth2_scheme())


@pytest.mark.asyncio
async def test_decode_jwt_invalid_token_raises():
    async def fake_oauth2_scheme():
        return "invalid.token.here"

    with pytest.raises(exceptions.CredentialsDataWrong):
        await jwt_utils.decode_jwt(token=await fake_oauth2_scheme())

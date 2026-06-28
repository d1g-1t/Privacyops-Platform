from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from src.application.dto.auth_dto import LoginRequest, TokenResponse, UserInfoResponse
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.presentation.deps import (
    CurrentUserId,
    get_auth_use_cases,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, response_class=ORJSONResponse)
async def login(
    body: LoginRequest,
    uc: AuthUseCases = Depends(get_auth_use_cases),
):
    return await uc.login(body)


@router.get("/me", response_model=UserInfoResponse, response_class=ORJSONResponse)
async def me(
    user_id: CurrentUserId,
    uc: AuthUseCases = Depends(get_auth_use_cases),
):
    return await uc.me(user_id)

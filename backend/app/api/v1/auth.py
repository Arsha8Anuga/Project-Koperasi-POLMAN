from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_current_user, get_db
from app.schemas.auth import LoginData, LoginRequest, PasswordChange
from app.schemas.common import ERROR_RESPONSES, ApiResponse
from app.schemas.user import UserOut
from app.services import auth_service
from app.utils.response import ok

router = APIRouter(prefix="/auth", tags=["auth"], responses=ERROR_RESPONSES)


@router.post("/login", response_model=ApiResponse[LoginData])
async def login(body: LoginRequest, db: AsyncDatabase = Depends(get_db)):
    return ok(await auth_service.login(db, body), "Login berhasil")


@router.get("/me", response_model=ApiResponse[UserOut])
async def me(user: CurrentUser = Depends(get_current_user), db: AsyncDatabase = Depends(get_db)):
    return ok(await auth_service.me(db, user))


@router.post("/logout", response_model=ApiResponse[None])
async def logout(user: CurrentUser = Depends(get_current_user), db: AsyncDatabase = Depends(get_db)):
    await auth_service.logout(db, user)
    return ok(None, "Logout berhasil")


@router.put("/password", response_model=ApiResponse[None])
async def change_password(
    body: PasswordChange, user: CurrentUser = Depends(get_current_user), db: AsyncDatabase = Depends(get_db)
):
    await auth_service.change_password(db, user, body)
    return ok(None, "Password berhasil diubah")

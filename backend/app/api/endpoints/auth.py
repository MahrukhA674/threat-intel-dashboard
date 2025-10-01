from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Register a new user."""
    return await AuthService.create_user(user, db)

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """Login to get access token."""
    user = await AuthService.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await AuthService.login(user)
    return Token(access_token=access_token)

@router.post("/logout")
async def logout(
    token: str = Depends(AuthService.get_current_user)
) -> dict:
    """Logout and invalidate token."""
    await AuthService.logout(token)
    return {"message": "Successfully logged out"}

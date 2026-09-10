from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendOtpRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.otp_service import issue_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_token_pair(user_id: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    existing = await User.find_one(User.email == payload.email)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is already registered.")

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
    )
    await user.insert()
    await issue_otp(user.id, user.email, "registration")

    return MessageResponse(
        message="Registration successful. Check your email for the verification code."
    )


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(payload: VerifyEmailRequest):
    user = await User.find_one(User.email == payload.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if user.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is already verified.")

    await verify_otp(user.id, "registration", payload.code)

    user.is_verified = True
    await user.save()

    return _issue_token_pair(str(user.id))


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(payload: ResendOtpRequest):
    user = await User.find_one(User.email == payload.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if payload.purpose == "registration" and user.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is already verified.")

    await issue_otp(user.id, user.email, payload.purpose)
    return MessageResponse(message="A new code has been sent.")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await User.find_one(User.email == payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")
    if not user.is_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Please verify your email before logging in."
        )

    return _issue_token_pair(str(user.id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    invalid_token_error = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token."
    )
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise invalid_token_error
    except JWTError:
        raise invalid_token_error

    user = await User.get(PydanticObjectId(data.get("sub")))
    if not user:
        raise invalid_token_error

    return _issue_token_pair(str(user.id))


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest):
    user = await User.find_one(User.email == payload.email)
    # Always return the same message whether or not the email exists —
    # avoids leaking which emails are registered.
    if user:
        await issue_otp(user.id, user.email, "password_reset")
    return MessageResponse(message="If that email is registered, a reset code has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest):
    user = await User.find_one(User.email == payload.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")

    await verify_otp(user.id, "password_reset", payload.code)

    user.hashed_password = hash_password(payload.new_password)
    await user.save()

    return MessageResponse(message="Password reset successful. Please log in.")

from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from app.models.user_role import SysUserRole
from app.models.role import SysRole
from app.core.database import SessionLocal
from typing import List

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("userId")
        email: str = payload.get("email")

        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Ambil user dari DB berdasarkan user_id
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            # Ambil role dari sys_user_roles
            role_record = (
                db.query(SysRole.code)
                .join(SysUserRole, SysRole.id == SysUserRole.role_id)
                .filter(SysUserRole.user_id == user_id)
                .first()
            )
            role = role_record.code if role_record else None

            return {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "role": role
            }
        finally:
            db.close()

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_role(required_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if not user_role or user_role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
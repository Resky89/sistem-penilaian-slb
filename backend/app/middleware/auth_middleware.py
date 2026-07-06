from functools import wraps
from flask import request, g
from app.controllers.auth import AuthController
from app.database.connection import get_session
from app.utils.exceptions import HTTPException, status

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token autentikasi tidak valid atau tidak disediakan"
            )
        
        token = auth_header.replace("Bearer ", "")
        db = get_session()
        try:
            # Panggil get_current_user secara langsung
            user = AuthController.get_current_user(token=token, db=db)
            g.current_user = user
            g.db = db
            return f(*args, **kwargs)
        except HTTPException as e:
            # Re-raise HTTPException ke global error handler
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token dekripsi gagal: {str(e)}"
            )
        finally:
            db.close()
    return decorated

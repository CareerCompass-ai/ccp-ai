from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt

import constant.config as cfg_constant
import constant.auth as auth_constant

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in auth_constant.WHITELIST_PATHS:  # Whitelist paths that don't require auth
            response = await call_next(request)
            return response
        
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
        else:
            return JSONResponse({"detail": "Authorization header missing"}, status_code=401)
        
        try:
            payload = jwt.decode(token, cfg_constant.JWT_SECRET_KEY, algorithms=[cfg_constant.JWT_ALGORITHM])
            # Store user info in request state if needed, e.g., request.state.user = payload
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token has expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
        
        response = await call_next(request)
        return response

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt

import constant.config as cfg_constant
import constant.auth as auth_constant

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in auth_constant.WHITELIST_PATHS:
            return await call_next(request)  # Allow access to whitelisted paths without auth

        if request.method == "OPTIONS":
            return await call_next(request)  # Allow preflight requests
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Authorization header missing or invalid"}, status_code=401)
        
        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, cfg_constant.JWT_SECRET_KEY, algorithms=[cfg_constant.JWT_ALGORITHM])
            request.state.user = payload  # Store user info in request state if needed

            authorized = self.check_authorization(request, payload)
            if not authorized:
                return JSONResponse({"detail": "You are not authorized to access this resource"}, status_code=403)
        
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token has expired"}, status_code=401)
        except (jwt.InvalidTokenError, IndexError, KeyError):
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
        
        response = await call_next(request)
        return response
    
    def check_authorization(self, request, payload):
        current_path = request.url.path

        # Check if the path requires admin role
        if current_path in auth_constant.ADMIN_PATHS:
            if payload.get("role") != "ADMIN":
                return False
            else:
                return True

        # For paths that require specific user_id or recruiter_id
        path_checks = {
            "/api/resumes": ("candidate_id", payload["userId"]),
            "/api/candidate/applied": ("candidate_id", payload["userId"]),
            "/api/candidate/update-saved-job": ("candidate_id", payload["userId"]),
            "/api/candidate/saved-jobs": ("candidate_id", payload["userId"]),
            "/api/recruiter/jobs-posted": ("recruiter_id", payload["userId"]),
            "/api/recruiter/update-saved-talent": ("recruiter_id", payload["userId"]),
            "/api/recruiter/candidates-saved": ("recruiter_id", payload["userId"]),
            "/api/recommend-jobs": ("user_id", payload["userId"]),
            "/api/job/create": ("recruiter_id", payload["userId"]),
            "/api/job/apply": ("candidate_id", payload["userId"]),
            "/api/job/close": ("recruiter_id", payload["userId"]),
            "/api/job/update": ("recruiter_id", payload["userId"]),
            "/api/job/applied-resumes": ("recruiter_id", payload["userId"]),
            "/api/resume/create": ("candidate_id", payload["userId"]),
            "/api/resume/delete": ("candidate_id", payload["userId"]),
        }
        
        if current_path in path_checks:
            param_name, expected_value = path_checks[current_path]
            param_value = request.query_params.get(param_name)
            if param_value and str(expected_value) == str(param_value):
                return True
        
        return False
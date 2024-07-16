from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import FormData
import jwt
import json
from io import BytesIO
from starlette.datastructures import UploadFile

import constant.config as cfg_constant
import constant.auth as auth_constant

class CustomRequest(Request):
    def __init__(self, scope, receive, body=None, form=None):
        super().__init__(scope, receive)
        self._body = body
        self._form = form

    async def body(self):
        if self._body is None:
            self._body = await super().body()
        return self._body

    async def json(self):
        body = await self.body()
        return json.loads(body)

    async def form(self):
        if self._form is None:
            form_data = await super().form()
            form_dict = dict(form_data)
            self._form = FormData([(key, value if isinstance(value, UploadFile) else BytesIO(value)) for key, value in form_dict.items()])
        return self._form

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

            # Create a CustomRequest object to store body and form data
            body = await request.body()
            form = await request.form()
            custom_request = CustomRequest(request.scope, request.receive, body, form)
            
            authorized = await self.check_authorization(custom_request, payload)
            if not authorized:
                return JSONResponse({"detail": "You are not authorized to access this resource"}, status_code=403)
        
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token has expired"}, status_code=401)
        except (jwt.InvalidTokenError, IndexError, KeyError):
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
        
        response = await call_next(custom_request)
        return response
    
    async def check_authorization(self, request, payload):
        current_path = request.url.path

        # Check if the path requires admin role
        if current_path in auth_constant.ADMIN_PATHS:
            if payload.get("role") != "ADMIN":
                return False
            else:
                return True
            
        # Check if the path requires recruiter role
        if current_path in auth_constant.RECRUITER_PAHTS:
            if payload.get("role") != "RECRUITER":
                return False
            else:
                return True

        if current_path in auth_constant.PATH_CHECKS_BODY:
            param_name = auth_constant.PATH_CHECKS_BODY[current_path]
            param_value = await self.get_param_value_from_body(request, param_name)
            if param_value and str(payload["userId"]) == str(param_value):
                return True
            else:
                return False
        
        if current_path in auth_constant.PATH_CHECKS_FORM_DATA:
            param_name = auth_constant.PATH_CHECKS_FORM_DATA[current_path]
            param_value = await self.get_param_value_from_form_data(request, param_name)
            if param_value and str(payload["userId"]) == str(param_value):
                return True
            else:
                return False

        if current_path in auth_constant.PATH_CHECKS_QUERY_PARAMS:
            param_name = auth_constant.PATH_CHECKS_QUERY_PARAMS[current_path]
            param_value = request.query_params.get(param_name)
            if param_value and str(payload["userId"]) == str(param_value):
                return True
            else:
                return False
        
        return True

    async def get_param_value_from_body(self, request, param_name):
        body = await request.json()
        return body.get(param_name)

    async def get_param_value_from_form_data(self, request, param_name):
        form = await request.form()
        return form.get(param_name)

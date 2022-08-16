from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.token import InvalidTokenModel



class DisallowBlacklistedTokens:
    async def __call__(self, request: Request, call_next):
        auth_header = request.headers.get('Authorization')
        try:
            _, token = auth_header.split()
            invalid_token =  await InvalidTokenModel.objects.get_or_none(token=token)
            if invalid_token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={'detail': 'Unauthorized'}
                    )
        except:
            pass
        
        # process the request and get the response    
        response = await call_next(request)
        return response

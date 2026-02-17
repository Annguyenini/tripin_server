from src.token.tokenservice import TokenService
def token_validation (token)->tuple: 
    tokenService = TokenService()
    status,message,code = tokenService.jwt_verify(token=token)
    return {'status':status,'message':message,'code':code}
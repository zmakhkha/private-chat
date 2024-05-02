from channels.db import database_sync_to_async
import jwt
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.conf import settings
from urllib.parse import parse_qs
from userman.models import Player
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
# from settings import SIMPLE_JWT, SECRET_KEY
from urllib.parse import parse_qs
import jwt




@database_sync_to_async
def get_user(token_key):
    # If you are using normal token based authentication
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

    # If you are using jwt
    try:
        user_id: int = jwt.decode(token_key, SECRET_KEY, algorithms=[SIMPLE_JWT['ALGORITHM']]).get(SIMPLE_JWT['USER_ID_CLAIM'])
    except jwt.exceptions.DecodeError:
        return AnonymousUser()
    except jwt.exceptions.ExpiredSignatureError:
        return AnonymousUser()
    try:
        return AnonymousUser() if user_id is None else User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()



class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)
    
    
    
    
    
    
    
# If you use djangochannel version 4 with django version 4 do this:
# Async function for find or create user that send a token with decoded that token
@database_sync_to_async
def get_or_create_user(token):
    try:
        # Decode a token that is send
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        # and other attrb that you want to get from payload

        # Query for find that user
        user = User.objects.filter(user_id=user_id).first()
        if user:
            # return the user we find from the query
            return user
        
        # We create a user with the attrb in given token
        user = User()
        user.id = user_id
        # and other attrb that you get from payload
        # save the obj
        user.save()
        return user

    # for handeling different errors in the consumer.py file
    except jwt.InvalidSignatureError:
        error = "InvalidSignatureError"
        return error
    
    except jwt.exceptions.DecodeError:
        error = "DecodeError" 
        return error

    except jwt.exceptions.ExpiredSignature:
        error = "ExpiredSignature" 
        return error
    
    except jwt.InvalidTokenError:
        error = "InvalidTokenError"
        return error




# A middleware for find a user by token (header or query_params)
class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        # Convert a scope to a dict for simplesidy
        # with header
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode("utf-8")
            auth_parts = auth_header.split()
            if len(auth_parts) == 2:
                # for remove a prefix that token

                _, token = auth_parts

                if token is not None:
                    user = await get_or_create_user(token)
                    if user is not None:
                        scope["user"] = user

            else:
                token = auth_header

                if token is not None:
                    user = await get_or_create_user(token)
                    print(user)
                    if user is not None:
                        scope["user"] = user
                        print(scope["user"])
                    else:
                        scope["user"] = AnonymousUser
                else:
                    scope["user"] = None
                

        # with query_params
        else:
            query_string = scope.get("query_string").decode("utf-8")
            # convet to the dict
            params = parse_qs(query_string)
            token = params.get("token")
            if token:
                token = token[0]
                user = await get_or_create_user(token)
                if user is not None:
                    # We set scope["user"] to the user is decode by this middlware for consumer
                    # this is a user obj or error message 
                    scope["user"] = user
            else:
                # we send a error to the client to send a token for connection
                scope["user"] = None

        return await self.inner(scope, receive, send)
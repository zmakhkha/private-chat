from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.management.utils import get_random_secret_key
import jwt
import json
import logging
from environ import Env

logger = logging.getLogger(__name__)
SECRET_KEY = get_random_secret_key()

env = Env()
env.read_env()
# SECRET_KEY = env("JWT_SECRET_KEY")

def create_response(request_id, code, message):
    try:
        req = str(request_id)
        data = {"data": message, "code": int(code), "request_id": req}
        return data
    except Exception as creation_error:
        logger.error(f'create_response:{creation_error}')

class JwtMiddleware(MiddlewareMixin):
    def process_request(self, request):
        jwt_token = request.headers.get('Authorization', None)
        logger.info(f"request received for endpoint {str(request.path)}")

        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('id')
                if user_id:
                    user = User.objects.get(pk=user_id)
                    request.user = user
                    return None
                else:
                    raise jwt.InvalidTokenError("User ID not found in token")
            except jwt.ExpiredSignatureError:
                response = create_response("", 4001, {"message": "Authentication token has expired"})
                logger.info(f"Response {response}")
                return HttpResponse(json.dumps(response), status=401)
            except jwt.InvalidTokenError as e:
                response = create_response("", 4001, {"message": f"Authorization has failed: {str(e)}"})
                logger.info(f"Response {response}")
                return HttpResponse(json.dumps(response), status=401)
            except User.DoesNotExist:
                response = create_response("", 4001, {"message": "User does not exist"})
                logger.info(f"Response {response}")
                return HttpResponse(json.dumps(response), status=401)
        else:
            response = create_response(
                "", 4001, {"message": "Authorization not found, Please send valid token in headers"}
            )
            logger.info(f"Response {response}")
            return HttpResponse(json.dumps(response), status=401)

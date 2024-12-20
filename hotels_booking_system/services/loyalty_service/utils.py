import jwt
import requests
import os
from service_errors import *

JWKS_URL = f"http://{os.environ.get('KC_HOST')}/realms/{os.environ.get('KC_REALM')}/protocol/openid-connect/certs"
CLIENT_ID = {os.environ.get('KC_CLIENT_ID')}  # audience


def get_signing_key(jwt_token):
    response = requests.get(JWKS_URL)
    jwks = response.json()
    header = jwt.get_unverified_header(jwt_token)
    kid = header.get("kid")

    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)

    raise ValueError("No matching key found in JWKS")


def check_jwt(bearer):
    try:
        jwt_token = bearer.split()[0]
        signing_key = get_signing_key(jwt_token)
        data = jwt.decode(
            jwt_token,
            signing_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            options={"verify_exp": False}
        )
        return data["name"]
    except:
        return error

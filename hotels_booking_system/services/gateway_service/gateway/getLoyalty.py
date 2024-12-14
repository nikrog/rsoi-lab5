import os
import json

from quart import Blueprint, Response, request
from .serviceRequests import get_data_from_service

getloyaltyb = Blueprint('get_loyalty', __name__, )


@getloyaltyb.route('/api/v1/loyalty', methods=['GET'])
async def get_loyalty() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['User Name missing']}))

    response = get_data_from_service('http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
        'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty', timeout=5,
                                     headers={'X-User-Name': request.headers['X-User-Name']})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service is unavailable']}))

    loyalty = response.json()

    return Response(status=200, content_type='application/json', response=json.dumps(loyalty))

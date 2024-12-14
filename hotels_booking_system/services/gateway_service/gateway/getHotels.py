import os
import json

from quart import Blueprint, Response, request
from .serviceRequests import get_data_from_service

gethotelsb = Blueprint('get_hotels', __name__, )


@gethotelsb.route('/api/v1/hotels', methods=['GET'])
async def get_hotels() -> Response:
    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':'
        + os.environ['RESERVATION_SERVICE_PORT'] + '/' + 'api/v1/hotels?' + request.full_path.split('?')[-1], timeout=5)

    if response:
        return Response(status=response.status_code, content_type='application/json', response=response.text)
    else:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))

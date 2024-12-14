import os
import json

from quart import Blueprint, Response, request
from .serviceRequests import get_data_from_service

getmeb = Blueprint('get_me', __name__, )


@getmeb.route('/api/v1/me', methods=['GET'])
async def get_me() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['User name missing']}))

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations',
        timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    reservations = response.json()
    for res in reservations:
        response = get_data_from_service(
            'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' +
            res['hotel_id'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Reservation service not working']}))

        del res['hotel_id']
        res['hotel'] = response.json()

        response = get_data_from_service('http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ[
            'PAYMENT_SERVICE_PORT'] + '/api/v1/payment/' + res['paymentUid'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Payment service not working']}))

        del res['paymentUid']
        res['payment'] = response.json()

    response = get_data_from_service('http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
        'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty', timeout=5,
                                     headers={'X-User-Name': request.headers['X-User-Name']})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service is unavailable']}))

    loyalty = response.json()
    result = {
        'reservations': reservations,
        'loyalty': loyalty
    }
    return Response(status=200, content_type='application/json', response=json.dumps(result))

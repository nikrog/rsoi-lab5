import os
import json

from quart import Blueprint, Response, request
from .serviceRequests import get_data_from_service

getreservationb = Blueprint('get_reservation', __name__, )


@getreservationb.route('/api/v1/reservations/<string:reservationUid>', methods=['GET'])
async def get_reservation(reservationUid: str) -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['User Name missing']}))

    response = get_data_from_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ[
        'RESERVATION_SERVICE_PORT'] + '/api/v1/reservations/' + reservationUid, timeout=5,
                                     headers={'X-User-Name': request.headers['X-User-Name']})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))

    if response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    reservation = response.json()

    response = get_data_from_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ[
        'RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' + reservation['hotel_id'], timeout=5,
                                     headers={'X-User-Name': request.headers['X-User-Name']})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))
    if response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    del reservation['hotel_id']
    reservation['hotel'] = response.json()

    response = get_data_from_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT'] + '/api/v1/payment/'
        + reservation['paymentUid'], timeout=5)
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Payment service is unavailable']}))

    del reservation['paymentUid']
    reservation['payment'] = response.json()

    return Response(status=200, content_type='application/json', response=json.dumps(reservation))

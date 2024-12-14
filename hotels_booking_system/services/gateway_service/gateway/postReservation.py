import os
import json
from datetime import datetime as dt

from quart import Blueprint, Response, request
from .serviceRequests import post_data_to_service, delete_data_from_service, get_data_from_service, \
    patch_data_to_service

postreservationb = Blueprint('post_reservation', __name__, )


def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['json load error']

    errors = []
    if ('hotelUid' not in body or type(body['hotelUid']) is not str) or (
            'startDate' not in body or type(body['startDate']) is not str) or (
            'endDate' not in body or type(body['endDate']) is not str):
        return None, ['wrong structure']

    return body, errors


@postreservationb.route('/api/v1/reservations', methods=['POST'])
async def post_reservations() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['User name missing']}))

    body, errors = validate_body(await request.body)
    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps(errors))

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' + body[
            'hotelUid'], timeout=5)

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    if response.status_code == 404:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    hotel = response.json()
    price = (dt.strptime(body['endDate'], "%Y-%m-%d").date() - dt.strptime(
        body['startDate'], "%Y-%m-%d").date()).days * hotel['price']

    response = get_data_from_service(
        'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ['LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
        timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    if response.status_code == 404:
        response2 = post_data_to_service(
            'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
                'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
            timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})
        if response2 is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Loyalty service not working']}))
        loyalty = response.json()
    else:
        loyalty = response.json()

    discount = loyalty['discount']

    price_with_discount = int(price * (1 - discount / 100))

    response = post_data_to_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT'] + '/api/v1/payment',
        timeout=5, headers={'X-User-Name': request.headers['X-User-Name']}, data={'price': price_with_discount})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Payment service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    payment = response.json()

    response = patch_data_to_service(
        'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ['LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
        timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service not working']}))

    if response.status_code == 404 or response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    loyalty = response.json()

    response = post_data_to_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations',
                                      timeout=5, headers={'X-User-Name': request.headers['X-User-Name']},
                                      data={'hotelUid': hotel['hotelUid'], 'startDate': body['startDate'],
                                            'endDate': body['endDate'],
                                            'paymentUid': payment['paymentUid']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    reservation = response.json()

    del reservation['hotel_id']
    reservation['hotelUid'] = hotel['hotelUid']
    del reservation['username']
    reservation['discount'] = discount
    del reservation['paymentUid']
    del payment['paymentUid']
    reservation['payment'] = payment

    return Response(status=200, content_type='application/json', response=json.dumps(reservation))

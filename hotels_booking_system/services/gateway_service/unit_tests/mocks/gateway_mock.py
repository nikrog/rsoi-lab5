import json
from quart import Response


def get_hotels() -> Response:
    response = {
        'status_code': 200,
        'text': {
            'hotelUid': "049161bb-badd-4fa8-9d90-87c9a82b0668",
            'name': "Ararat Park Hyatt Moscow",
            'country': "Россия",
            'city': "Москва",
            'address': "Неглинная ул., 4",
            'stars': 5,
            'price': 10000
        }}

    if response:
        return Response(status=response['status_code'], content_type='application/json', response=response['text'])
    else:
        return Response(status=503, content_type='application/json',
                        response=json.dumps({'message': 'Reservation Service unavailable'}))


def get_loyalty(username: str) -> Response:
    if username != "Test Max":
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'message': 'User Name missing'}))
    loyalty = {
        'reservation_count': 25,
        'status': "GOLD",
        'discount': 10}
    if loyalty is None:
        return Response(status=503, content_type='application/json',
                        response=json.dumps({'message': 'Loyalty Service unavailable'}))

    return Response(status=200, content_type='application/json', response=json.dumps(loyalty))


def get_reservation(reservationUid: str, username: str) -> Response:
    if username != "Test Max":
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'message': 'User Name missing'}))

    response = {
        'status_code': 200,
        'text': {'hotel_id': 1,
                 'paymentUid': '049161bb-badd-4fa8-9d90-87c9a82b0111'}
    }

    if response is None:
        return Response(status=503, content_type='application/json',
                        response=json.dumps({'message': 'Reservation Service unavailable'}))

    if response['status_code'] != 200:
        return Response(status=response['status_code'], content_type='application/json',
                        response=json.dumps(response['text']))

    reservation = response['text']

    response = {
        'status_code': 200,
        'text': {'name': 'Ararat Park Hyatt Moscow',
                 'address': 'Россия, Москва, Неглинная ул., 4',
                 'stars': 5}
    }

    if response is None:
        return Response(status=503, content_type='application/json',
                        response=json.dumps({'message': 'Reservation Service unavailable'}))
    if response['status_code'] != 200:
        return Response(status=response['status_code'], content_type='application/json',
                        response=json.dumps(response['text']))

    del reservation['hotel_id']
    reservation['hotel'] = response['text']

    response = {
        'status_code': 200,
        'text': {'status': 'PAID',
                 'price': 50000}
    }

    del reservation['paymentUid']

    if response is None:
        reservation['payment'] = {}
    elif response['status_code'] != 200:
        return Response(status=response['status_code'], content_type='application/json',
                        response=json.dumps(response['text']))
    else:
        reservation['payment'] = response['text']

    return Response(status=200, content_type='application/json', response=json.dumps(reservation))

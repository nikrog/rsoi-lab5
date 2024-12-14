import datetime
import json
import uuid
from quart import Blueprint, Response, request
from reservation.models.models_class import ReservationModel, HotelsModel

postreservationb = Blueprint('post_cur_reservation', __name__, )


def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['wrong']

    errors = []

    if (('hotelUid' not in body or type(body['hotelUid']) is not str) or (
            'startDate' not in body or type(body['startDate']) is not str) or (
            'endDate' not in body or type(body['endDate']) is not str) or (
            'paymentUid' not in body or type(body['paymentUid']) is not str)):
        return None, ['Bad structure body!']

    return body, errors


@postreservationb.route('/api/v1/reservations', methods=['POST'])
async def post_reservation() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']

    body, errors = validate_body(await request.body)
    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps(errors))

    hotel = HotelsModel.select().where(HotelsModel.hotel_uid == body['hotelUid']).get()

    reservation = ReservationModel.create(
        reservation_uid=uuid.uuid4(),
        username=user,
        payment_uid=uuid.UUID(body['paymentUid']),
        hotel_id=hotel.id,
        #hotel_id=hotel['hotel_id'],
        status='PAID',
        start_date=datetime.datetime.strptime(body['startDate'], "%Y-%m-%d").date(),
        end_date=datetime.datetime.strptime(body['endDate'], "%Y-%m-%d").date(),
    )

    return Response(status=200, content_type='application/json', response=json.dumps(reservation.to_dict()))

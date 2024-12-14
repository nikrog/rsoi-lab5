import json
from quart import Blueprint, Response, request
from reservation.models.models_class import ReservationModel

getreservationsb = Blueprint('get_cur_reservations', __name__,)


@getreservationsb.route('/api/v1/reservations', methods=['GET'])
async def get_reservations() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']
    reservations = [reservation.to_dict() for reservation in ReservationModel.select().where(ReservationModel.username == user)]

    return Response(status=200, content_type='application/json', response=json.dumps(reservations))

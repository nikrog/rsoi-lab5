import json
from quart import Blueprint, Response, request
from reservation.models.models_class import ReservationModel

getcurreservationb = Blueprint('get_cur_reservation', __name__,)


@getcurreservationb.route('/api/v1/reservations/<string:reservationUid>', methods=['GET'])
async def get_reservation(reservationUid: str) -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']
    #reservation = ReservationModel.select().where((ReservationModel.username == user)
    # & (ReservationModel.reservation_uid == reservationUid)).get().to_dict()
    try:
        reservation = ReservationModel.select().where(ReservationModel.reservation_uid == reservationUid).get().to_dict()

        return Response(status=200, content_type='application/json', response=json.dumps(reservation))

    except:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['reservation not found']}))
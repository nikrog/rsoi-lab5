import json
from quart import Blueprint, Response, request
from reservation.models.models_class import ReservationModel

deletereservationb = Blueprint('delete_current_reservation', __name__,)


@deletereservationb.route('/api/v1/reservations/<string:reservationUid>', methods=['DELETE'])
async def delete_reservation(reservationUid: str) -> Response:
    try:
        reservation = ReservationModel.select().where(ReservationModel.reservation_uid == reservationUid).get()

        if reservation.status != 'PAID':
            return Response(status=403, content_type='application/json',
                            response=json.dumps({'message': ['Reservation not paid.']}))

        reservation.status = 'CANCELED'
        reservation.save()

        return Response(status=200, content_type='application/json', response=json.dumps(reservation.to_dict()))
    except Exception as e:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['Reservation not found']}))

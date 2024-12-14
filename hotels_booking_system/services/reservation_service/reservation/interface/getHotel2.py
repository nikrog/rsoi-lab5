import json
from quart import Blueprint, Response
from reservation.models.models_class import HotelsModel

gethotel2b = Blueprint('get_hotel2', __name__, )


@gethotel2b.route('/api/v1/hotels/<string:hotelUid>', methods=['GET'])
async def get_hotel(hotelUid: str) -> Response:
    try:
        hotel = HotelsModel.select().where(HotelsModel.hotel_uid == hotelUid).get().to_dict()
        return Response(status=200, content_type='application/json', response=json.dumps(hotel))
    except:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['Hotel not found']}))

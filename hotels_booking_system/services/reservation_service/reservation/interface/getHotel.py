import json
from quart import Blueprint, Response
from reservation.models.models_class import HotelsModel

gethotelb = Blueprint('get_hotel', __name__, )


@gethotelb.route('/api/v1/hotels/<int:hotelId>', methods=['GET'])
async def get_hotel(hotelId: int) -> Response:
    try:
        hotel = HotelsModel.select().where(HotelsModel.id == hotelId).get().to_dict_short()
        return Response(status=200, content_type='application/json', response=json.dumps(hotel))
    except:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['Hotel not found']}))

import json
from quart import Blueprint, Response, request
from loyalty.models.models_class import LoyaltyModel

getloyaltyb = Blueprint('get_loyalty', __name__,)


@getloyaltyb.route('/api/v1/loyalty', methods=['GET'])
async def get_loyalty() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']
    loyalty = LoyaltyModel.select().where(LoyaltyModel.username == user).get().to_dict()

    if loyalty is not None:
        return Response(status=200, content_type='application/json', response=json.dumps(loyalty))
    else:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['user not found']}))


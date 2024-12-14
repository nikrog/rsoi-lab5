import json
from quart import Blueprint, Response, request
from loyalty.models.models_class import LoyaltyModel, loyalty_dict

postloyaltyb = Blueprint('post_loyalty', __name__, )


@postloyaltyb.route('/api/v1/loyalty', methods=['POST'])
async def post_loyalty() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']

    loyalty = LoyaltyModel.create(username=user,
                                  reservation_count=0,
                                  status='BRONZE',
                                  discount=loyalty_dict['BRONZE']['discount'])

    return Response(status=200, content_type='application/json', response=json.dumps(loyalty.to_dict()))

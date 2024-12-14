import json
from quart import Blueprint, Response, request
from loyalty.models.models_class import LoyaltyModel, loyalty_dict

patchloyaltyb = Blueprint('patch_loyalty', __name__, )


@patchloyaltyb.route('/api/v1/loyalty', methods=['PATCH'])
async def patch_loyalty() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(status=400, content_type='application/json',
                        response=json.dumps({'errors': ['user not found']}))

    user = request.headers['X-User-Name']

    try:
        loyalty = LoyaltyModel.select().where(LoyaltyModel.username == user).get()
        loyalty.reservation_count += 1
        if loyalty.reservation_count >= loyalty_dict['GOLD']['min_reservations_count']:
            loyalty.status = 'GOLD'
            loyalty.discount = loyalty_dict['GOLD']['discount']
        elif loyalty.reservation_count >= loyalty_dict['SILVER']['min_reservations_count']:
            loyalty.status = 'SILVER'
            loyalty.discount = loyalty_dict['SILVER']['discount']
        loyalty.save()

        return Response(status=200, content_type='application/json', response=json.dumps(loyalty.to_dict()))
    except Exception as e:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty not found']}))

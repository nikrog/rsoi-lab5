import json
from quart import Blueprint, Response, request
from reservation.models.models_class import HotelsModel

gethotelsb = Blueprint('get_hotels', __name__, )


def validate_args(args):
    errors = []
    if 'page' in args.keys():
        try:
            page = int(args['page'])
            if page <= 0:
                errors.append('wrong page number')
        except ValueError:
            errors.append('page should be a number')
            page = None
    else:
        errors.append('enter page number')
        page = None

    if 'size' in args.keys():
        try:
            size = int(args['size'])
            if size <= 0 or size > 100:
                errors.append('wrong size number')
        except ValueError:
            size = None
            errors.append('size should be a number')
    else:
        errors.append('enter size number')
        size = None

    return page, size, errors


@gethotelsb.route('/api/v1/hotels', methods=['GET'])
async def get_hotels() -> Response:
    page, size, errors = validate_args(request.args)

    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps({'errors': errors}))

    count_total = HotelsModel.select().count()
    hotels = [hotel.to_dict() for hotel in HotelsModel.select().paginate(page, size)]

    return Response(status=200, content_type='application/json',
                    response=json.dumps({"page": page, "pageSize": size, "totalElements": count_total, "items": hotels}))
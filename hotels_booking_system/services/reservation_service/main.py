import json
import uuid
import os
import datetime as dt
from flask import Flask, request, make_response, jsonify, Response
from authlib.integrations.flask_client import OAuth
from models.models_class import ReservationModel, HotelsModel
from utils import *


def create_tables():
    ReservationModel.drop_table()
    HotelsModel.drop_table()
    HotelsModel.create_table()
    ReservationModel.create_table()

    HotelsModel.get_or_create(
        id=1,
        hotel_uid="049161bb-badd-4fa8-9d90-87c9a82b0668",
        name="Ararat Park Hyatt Moscow",
        country="Россия",
        city="Москва",
        address="Неглинная ул., 4",
        stars=5,
        price=10000
    )

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
#app.secret_key = os.environ['APP_SECRET_KEY']

oauth = OAuth(app)
oauth.register(
    "keycloak",
    client_id=os.environ.get("KC_CLIENT_ID"),
    client_secret=os.environ.get("KC_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"http://{os.environ.get('KC_HOST')}/realms/{os.environ.get('KC_REALM')}/.well-known/openid-configuration",
)


@app.route("/")
def service():
    return "RESERVATION"

@app.route('/api/v1/hotels/<int:hotelId>', methods=['GET'])
def get_hotel(hotelId: int) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        hotel = HotelsModel.select().where(HotelsModel.id == hotelId).get().to_dict_short()
        return Response(status=200, content_type='application/json', response=json.dumps(hotel))
    except:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['Hotel not found']}))


@app.route('/api/v1/hotels/<string:hotelUid>', methods=['GET'])
def get_hotel2(hotelUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        hotel = HotelsModel.select().where(HotelsModel.hotel_uid == hotelUid).get().to_dict()
        return Response(status=200, content_type='application/json', response=json.dumps(hotel))
    except:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['Hotel not found']}))


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


@app.route('/api/v1/hotels', methods=['GET'])
def get_hotels() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    page, size, errors = validate_args(request.args)

    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps({'errors': errors}))

    count_total = HotelsModel.select().count()
    hotels = [hotel.to_dict() for hotel in HotelsModel.select().paginate(page, size)]

    return Response(status=200, content_type='application/json',
                    response=json.dumps({"page": page, "pageSize": size, "totalElements": count_total, "items": hotels}))


@app.route('/api/v1/reservations/<string:reservationUid>', methods=['GET'])
def get_reservation(reservationUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        reservation = ReservationModel.select().where(ReservationModel.reservation_uid == reservationUid).get().to_dict()

        return Response(status=200, content_type='application/json', response=json.dumps(reservation))

    except:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['reservation not found']}))


@app.route('/api/v1/reservations', methods=['GET'])
def get_reservations() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    reservations = [reservation.to_dict() for reservation in ReservationModel.select().where(ReservationModel.username == client)]

    return Response(status=200, content_type='application/json', response=json.dumps(reservations))


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


@app.route('/api/v1/reservations', methods=['POST'])
def post_reservation() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['user not found']}))
    #
    # user = request.headers['X-User-Name']

    body, errors = validate_body(request.get_data())
    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps(errors))

    hotel = HotelsModel.select().where(HotelsModel.hotel_uid == body['hotelUid']).get()

    reservation = ReservationModel.create(
        reservation_uid=uuid.uuid4(),
        username=client,
        payment_uid=uuid.UUID(body['paymentUid']),
        hotel_id=hotel.id,
        #hotel_id=hotel['hotel_id'],
        status='PAID',
        start_date=dt.datetime.strptime(body['startDate'], "%Y-%m-%d").date(),
        end_date=dt.datetime.strptime(body['endDate'], "%Y-%m-%d").date(),
    )

    return Response(status=200, content_type='application/json', response=json.dumps(reservation.to_dict()))


@app.route('/api/v1/reservations/<string:reservationUid>', methods=['DELETE'])
def delete_reservation(reservationUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

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


@app.route('/manage/health', methods=['GET'])
def health_check() -> Response:
    return Response(status=200)


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8070)

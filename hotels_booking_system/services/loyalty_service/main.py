from flask import Flask, Response, request
from authlib.integrations.flask_client import OAuth
import json
import os
from models.models_class import LoyaltyModel, loyalty_dict
from utils import *


def create_tables():
    LoyaltyModel.drop_table()
    LoyaltyModel.create_table()

    LoyaltyModel.get_or_create(
        id=1,
        username="Test Max",
        reservation_count=25,
        status="GOLD",
        discount=10
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
    server_metadata_url=f"http://{os.environ.get("KC_HOST")}/realms/{os.environ.get("KC_REALM")}/.well-known/openid-configuration",
)


@app.route("/")
def service():
    return "LOYALTY"


@app.route('/api/v1/loyalty', methods=['GET'])
def get_loyalty() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    loyalty = LoyaltyModel.select().where(LoyaltyModel.username == client).get().to_dict()

    if loyalty is not None:
        return Response(status=200, content_type='application/json', response=json.dumps(loyalty))
    else:
        return Response(status=404, content_type='application/json', response=json.dumps({'errors': ['user not found']}))


@app.route('/api/v1/loyalty', methods=['DELETE'])
def delete_loyalty() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        loyalty = LoyaltyModel.select().where(LoyaltyModel.username == client).get()
        if loyalty.reservation_count > 0:
            loyalty.reservation_count -= 1

        if loyalty.reservation_count < loyalty_dict['SILVER']['min_reservations_count']:
            loyalty.status = 'BRONZE'
            loyalty.discount = loyalty_dict['BRONZE']['discount']
        elif loyalty.reservation_count < loyalty_dict['GOLD']['min_reservations_count']:
            loyalty.status = 'SILVER'
            loyalty.discount = loyalty_dict['SILVER']['discount']
        loyalty.save()

        return Response(status=200, content_type='application/json', response=json.dumps(loyalty.to_dict()))
    except Exception as e:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['Loyalty not found']}))


@app.route('/api/v1/loyalty', methods=['PATCH'])
def patch_loyalty() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        loyalty = LoyaltyModel.select().where(LoyaltyModel.username == client).get()
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


@app.route('/api/v1/loyalty', methods=['POST'])
def post_loyalty() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    loyalty = LoyaltyModel.create(username=client,
                                  reservation_count=0,
                                  status='BRONZE',
                                  discount=loyalty_dict['BRONZE']['discount'])

    return Response(status=200, content_type='application/json', response=json.dumps(loyalty.to_dict()))


@app.route('/manage/health', methods=['GET'])
def health_check() -> Response:
    return Response(status=200)


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8050)

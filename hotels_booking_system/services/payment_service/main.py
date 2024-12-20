import json
import uuid
import os
from flask import Flask, request, make_response, jsonify, Response
from authlib.integrations.flask_client import OAuth
from models.models_class import PaymentModel
from utils import *

def create_tables():
    PaymentModel.drop_table()
    PaymentModel.create_table()


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
    return "PAYMENT"


@app.route('/api/v1/payment/<string:paymentUid>', methods=['GET'])
def get_payment(paymentUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        payment = PaymentModel.select().where(PaymentModel.payment_uid == paymentUid).get().to_dict()

        return Response(status=200, content_type='application/json', response=json.dumps(payment))
    except:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'errors': ['Payment not found']}))


def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['Error']

    errors = []
    if 'price' not in body.keys() or type(body['price']) is not int:
        return None, ['wrong structure']

    return body, errors


@app.route('/api/v1/payment', methods=['POST'])
def post_payment() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    body, errors = validate_body(request.get_data())

    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps(errors))

    payment = PaymentModel.create(payment_uid=uuid.uuid4(),
                                  price=body['price'],
                                  status='PAID')

    return Response(status=200, content_type='application/json', response=json.dumps(payment.to_dict_with_uid()))


@app.route('/api/v1/payment/<string:paymentUid>', methods=['DELETE'])
def delete_payment(paymentUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    try:
        payment = PaymentModel.select().where(PaymentModel.payment_uid == paymentUid).get()
        payment.status = 'CANCELED'
        payment.save()

        return Response(status=200, content_type='application/json', response=json.dumps(payment.to_dict()))
    except:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['Payment not found']}))


@app.route('/manage/health', methods=['GET'])
def health_check() -> Response:
    return Response(status=200)


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8060)

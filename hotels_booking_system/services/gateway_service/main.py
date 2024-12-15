from flask import Flask, request, make_response, jsonify, Response
import json
import os
from flask import redirect, render_template, session, url_for
from authlib.integrations.flask_client import OAuth
from datetime import datetime as dt
from serviceRequests import *
from utils import *

reservation_url = f"http://{os.environ['RESERVATION_SERVICE_HOST']}:{os.environ['RESERVATION_SERVICE_PORT']}"
payment_url = f"http://{os.environ['PAYMENT_SERVICE_HOST']}:{os.environ['PAYMENT_SERVICE_PORT']}"
loyalty_url = f"http://{os.environ['LOYALTY_SERVICE_HOST']}:{os.environ['LOYALTY_SERVICE_PORT']}"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
#app.secret_key = os.environ['APP_SECRET_KEY']

oauth = OAuth(app)
oauth.register(
    "keycloak",
    client_id='',
    client_secret='',
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"http://localhost:8080/realms/myrealm/.well-known/openid-configuration",
)

@app.route("/")
def service():
    return "GATEWAY"


@app.route('/api/v1/hotels', methods=['GET'])
def get_hotels() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':'
        + os.environ['RESERVATION_SERVICE_PORT'] + '/' + 'api/v1/hotels?' + request.full_path.split('?')[-1], timeout=5)

    if response:
        return Response(status=response.status_code, content_type='application/json', response=response.text)
    else:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))


@app.route('/api/v1/loyalty', methods=['GET'])
def get_loyalty() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['User Name missing']}))

    response = get_data_from_service('http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
        'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty', timeout=5,
                                     headers={'X-User-Name': client})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service is unavailable']}))

    loyalty = response.json()

    return Response(status=200, content_type='application/json', response=json.dumps(loyalty))


@app.route('/api/v1/me', methods=['GET'])
def get_me() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)

    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['User name missing']}))

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations',
        timeout=5, headers={'X-User-Name': client})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    reservations = response.json()
    for res in reservations:
        response = get_data_from_service(
            'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' +
            res['hotel_id'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Reservation service not working']}))

        del res['hotel_id']
        res['hotel'] = response.json()

        response = get_data_from_service('http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ[
            'PAYMENT_SERVICE_PORT'] + '/api/v1/payment/' + res['paymentUid'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Payment service not working']}))

        del res['paymentUid']
        res['payment'] = response.json()

    response = get_data_from_service('http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
        'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty', timeout=5,
                                     headers={'X-User-Name': client})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service is unavailable']}))

    loyalty = response.json()
    result = {
        'reservations': reservations,
        'loyalty': loyalty
    }
    return Response(status=200, content_type='application/json', response=json.dumps(result))


@app.route('/api/v1/reservations/<string:reservationUid>', methods=['GET'])
def get_reservation(reservationUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)
    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['User Name missing']}))

    response = get_data_from_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ[
        'RESERVATION_SERVICE_PORT'] + '/api/v1/reservations/' + reservationUid, timeout=5,
                                     headers={'X-User-Name': client})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))

    if response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    reservation = response.json()

    response = get_data_from_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ[
        'RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' + reservation['hotel_id'], timeout=5,
                                     headers={'X-User-Name': client})
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service is unavailable']}))
    if response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    del reservation['hotel_id']
    reservation['hotel'] = response.json()

    response = get_data_from_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT'] + '/api/v1/payment/'
        + reservation['paymentUid'], timeout=5)
    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Payment service is unavailable']}))

    del reservation['paymentUid']
    reservation['payment'] = response.json()

    return Response(status=200, content_type='application/json', response=json.dumps(reservation))


@app.route('/api/v1/reservations', methods=['GET'])
def get_reservations() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)
    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['User name missing']}))

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations',
        timeout=5, headers={'X-User-Name': client})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    reservations = response.json()
    for res in reservations:
        response = get_data_from_service(
            'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' +
            res['hotel_id'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Reservation service not working']}))

        del res['hotel_id']
        res['hotel'] = response.json()

        response = get_data_from_service('http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ[
            'PAYMENT_SERVICE_PORT'] + '/api/v1/payment/' + res['paymentUid'], timeout=5)

        if response is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Payment service not working']}))

        del res['paymentUid']
        res['payment'] = response.json()

    return Response(status=200, content_type='application/json', response=json.dumps(reservations))

def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['json load error']

    errors = []
    if ('hotelUid' not in body or type(body['hotelUid']) is not str) or (
            'startDate' not in body or type(body['startDate']) is not str) or (
            'endDate' not in body or type(body['endDate']) is not str):
        return None, ['wrong structure']

    return body, errors


@app.route('/api/v1/reservations', methods=['POST'])
def post_reservations() -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)
    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'errors': ['User name missing']}))

    body, errors = validate_body(request.get_data())
    if len(errors) > 0:
        return Response(status=400, content_type='application/json', response=json.dumps(errors))

    response = get_data_from_service(
        'http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/hotels/' + body[
            'hotelUid'], timeout=5)

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    if response.status_code == 404:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    hotel = response.json()
    price = (dt.strptime(body['endDate'], "%Y-%m-%d").date() - dt.strptime(
        body['startDate'], "%Y-%m-%d").date()).days * hotel['price']

    response = get_data_from_service(
        'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ['LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
        timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    if response.status_code == 404:
        response2 = post_data_to_service(
            'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ[
                'LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
            timeout=5, headers={'X-User-Name': request.headers['X-User-Name']})
        if response2 is None:
            return Response(status=500, content_type='application/json',
                            response=json.dumps({'errors': ['Loyalty service not working']}))
        loyalty = response.json()
    else:
        loyalty = response.json()

    discount = loyalty['discount']

    price_with_discount = int(price * (1 - discount / 100))

    response = post_data_to_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT'] + '/api/v1/payment',
        timeout=5, headers={'X-User-Name': client}, data={'price': price_with_discount})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Payment service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    payment = response.json()

    response = patch_data_to_service(
        'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ['LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
        timeout=5, headers={'X-User-Name': client})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Loyalty service not working']}))

    if response.status_code == 404 or response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    loyalty = response.json()

    response = post_data_to_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':' + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations',
                                      timeout=5, headers={'X-User-Name': client},
                                      data={'hotelUid': hotel['hotelUid'], 'startDate': body['startDate'],
                                            'endDate': body['endDate'],
                                            'paymentUid': payment['paymentUid']})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'errors': ['Reservation service not working']}))

    if response.status_code == 400:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    reservation = response.json()

    del reservation['hotel_id']
    reservation['hotelUid'] = hotel['hotelUid']
    del reservation['username']
    reservation['discount'] = discount
    del reservation['paymentUid']
    del payment['paymentUid']
    reservation['payment'] = payment

    return Response(status=200, content_type='application/json', response=json.dumps(reservation))


@app.route('/api/v1/reservations/<string:reservationUid>', methods=['DELETE'])
def delete_reservation(reservationUid: str) -> Response:
    bearer = request.headers.get('Authorization')

    if bearer is None:
        return Response(status=401)

    client = check_jwt(bearer)

    if not client:
        return Response(status=401)
    # if 'X-User-Name' not in request.headers.keys():
    #     return Response(status=400, content_type='application/json',
    #                     response=json.dumps({'message': ['User name missing']}))

    response = delete_data_from_service('http://' + os.environ['RESERVATION_SERVICE_HOST'] + ':'
                                        + os.environ['RESERVATION_SERVICE_PORT'] + '/api/v1/reservations/'
                                        + reservationUid, timeout=5)

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'message': ['Reservation service not working']}))
    elif response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    reservation = response.json()

    response = delete_data_from_service('http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':'
                                        + os.environ['PAYMENT_SERVICE_PORT'] + '/api/v1/payment/'
                                        + reservation['paymentUid'], timeout=5)

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'message': ['Payment service not working']}))

    elif response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    response = delete_data_from_service(
        'http://' + os.environ['LOYALTY_SERVICE_HOST'] + ':' + os.environ['LOYALTY_SERVICE_PORT'] + '/api/v1/loyalty',
        timeout=5, headers={'X-User-Name': client})

    if response is None:
        return Response(status=500, content_type='application/json',
                        response=json.dumps({'message': ['Loyalty service not working']}))

    elif response.status_code != 200:
        return Response(status=response.status_code, content_type='application/json', response=response.text)

    return Response(status=204)


@app.route('/manage/health', methods=['GET'])
def health_check() -> Response:
    return Response(status=200)


@app.route("/authorize")
def login():
    return oauth.keycloak.authorize_redirect(redirect_uri=url_for("callback", _external=True))


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.keycloak.authorize_access_token()
    session["user"] = token
    return redirect("/")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

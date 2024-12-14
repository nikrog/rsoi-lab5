import json
from quart import Blueprint, Response
from payments.models.models_class import PaymentModel

deletepaymentb = Blueprint('delete_current_payment', __name__,)

@deletepaymentb.route('/api/v1/payment/<string:paymentUid>', methods=['DELETE'])
async def delete_payment(paymentUid: str) -> Response:
    try:
        payment = PaymentModel.select().where(PaymentModel.payment_uid == paymentUid).get()
        payment.status = 'CANCELED'
        payment.save()

        return Response(status=200, content_type='application/json', response=json.dumps(payment.to_dict()))
    except:
        return Response(status=404, content_type='application/json',
                        response=json.dumps({'message': ['Payment not found']}))

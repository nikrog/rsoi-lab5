from quart import Quart
from payments.models.models_class import PaymentModel
from payments.interface.getPayment import getpaymentb
from payments.interface.postPayment import postpaymentb
from payments.interface.deletePayment import deletepaymentb
from payments.interface.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(getpaymentb)
app.register_blueprint(postpaymentb)
app.register_blueprint(deletepaymentb)
app.register_blueprint(healthcheckb)


def create_tables():
    PaymentModel.drop_table()
    PaymentModel.create_table()


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8060)

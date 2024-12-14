from quart import Quart
from gateway.getHotels import gethotelsb
from gateway.getMe import getmeb
from gateway.getReservations import getreservationsb
from gateway.getReservation import getreservationb
from gateway.postReservation import postreservationb
from gateway.deleteReservation import deletereservationb
from gateway.getLoyalty import getloyaltyb
from gateway.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(gethotelsb)
app.register_blueprint(getmeb)
app.register_blueprint(getreservationsb)
app.register_blueprint(getreservationb)
app.register_blueprint(postreservationb)
app.register_blueprint(deletereservationb)
app.register_blueprint(getloyaltyb)
app.register_blueprint(healthcheckb)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

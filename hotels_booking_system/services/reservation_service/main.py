from quart import Quart
from reservation.models.models_class import ReservationModel, HotelsModel
from reservation.interface.getHotels import gethotelsb
from reservation.interface.getHotel import gethotelb
from reservation.interface.getHotel2 import gethotel2b
from reservation.interface.getReservations import getreservationsb
from reservation.interface.getReservation import getcurreservationb
from reservation.interface.postReservation import postreservationb
from reservation.interface.deleteReservation import deletereservationb
from reservation.interface.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(gethotelsb)
app.register_blueprint(gethotelb)
app.register_blueprint(gethotel2b)
app.register_blueprint(getreservationsb)
app.register_blueprint(getcurreservationb)
app.register_blueprint(postreservationb)
app.register_blueprint(deletereservationb)
app.register_blueprint(healthcheckb)


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


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8070)

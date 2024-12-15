from peewee import *
from .models_db import BaseModel


class HotelsModel(BaseModel):
    id = IdentityField(primary_key=True)
    hotel_uid = UUIDField(unique=True, null=False)
    name = CharField(max_length=255, null=False)
    country = CharField(max_length=80, null=False)
    city = CharField(max_length=80, null=False)
    address = CharField(max_length=255, null=False)
    stars = IntegerField()
    price = IntegerField(null=False)

    def to_dict(self):
        return {
            'hotelUid': str(self.hotel_uid),
            'name': str(self.name),
            'country': str(self.country),
            'city': str(self.city),
            'address': str(self.address),
            'stars': self.stars,
            'price': self.price
        }

    def to_dict_short(self):
        return {
            'hotelUid': str(self.hotel_uid),
            'name': str(self.name),
            'fullAddress': str(self.country + ', ' + self.city + ', ' + self.address),
            'stars': self.stars
        }

    def to_dict_full(self):
        return {
            'hotelId': id,
            'hotelUid': str(self.hotel_uid),
            'name': str(self.name),
            'country': str(self.country),
            'city': str(self.city),
            'address': str(self.address),
            'stars': self.stars,
            'price': self.price
        }

    class Meta:
        db_table = 'hotels'


class ReservationModel(BaseModel):
    id = IdentityField(primary_key=True)
    reservation_uid = UUIDField(unique=True, null=False)
    username = CharField(max_length=80, null=False)
    payment_uid = UUIDField(null=False)
    hotel_id = ForeignKeyField(HotelsModel, to_field='id')
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('PAID', 'CANCELED')")])
    start_date = DateField(null=False, formats='%Y-%m-%d')
    end_date = DateField(null=False, formats='%Y-%m-%d')

    def to_dict(self):
        return {
            'reservationUid': str(self.reservation_uid),
            'username': str(self.username),
            'paymentUid': str(self.payment_uid),
            'hotel_id': str(self.hotel_id),
            'status': str(self.status),
            'startDate': str(self.start_date),
            'endDate': str(self.end_date)
        }

    class Meta:
        db_table = 'reservation'
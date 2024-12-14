from peewee import *
from .models_db import BaseModel

loyalty_dict = {'BRONZE': {"min_reservations_count": 0, "discount": 5},
                'SILVER': {"min_reservations_count": 10, "discount": 7},
                'GOLD': {"min_reservations_count": 20, "discount": 10}}


class LoyaltyModel(BaseModel):
    id = IdentityField(primary_key=True)
    username = CharField(max_length=80, unique=True, null=False)
    reservation_count = IntegerField(null=False, default=0)
    status = CharField(max_length=80, null=False, default='BRONZE',
                       constraints=[Check("status IN ('BRONZE', 'SILVER', 'GOLD')")])
    discount = IntegerField(null=False)

    def to_dict(self):
        return {
            'status': str(self.status),
            'discount': self.discount,
            'reservationCount': self.reservation_count
        }

    class Meta:
        db_table = 'loyalty'
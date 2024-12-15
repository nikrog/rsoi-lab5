from peewee import *
from .models_db import BaseModel


class PaymentModel(BaseModel):
    id = IdentityField(primary_key=True)
    payment_uid = UUIDField(null=False)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('PAID', 'CANCELED')")])
    price = IntegerField(null=False)

    def to_dict(self):
        return {
            'status': str(self.status),
            'price': self.price
        }

    def to_dict_with_uid(self):
        return {
            'status': str(self.status),
            'price': self.price,
            'paymentUid': str(self.payment_uid)
        }

    class Meta:
        db_table = 'payment'

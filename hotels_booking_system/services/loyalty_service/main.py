from quart import Quart
from loyalty.models.models_class import LoyaltyModel
from loyalty.interface.getLoyalty import getloyaltyb
from loyalty.interface.postLoyalty import postloyaltyb
from loyalty.interface.patchLoyalty import patchloyaltyb
from loyalty.interface.deleteLoyalty import deleteloyaltyb
from loyalty.interface.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(getloyaltyb)
app.register_blueprint(postloyaltyb)
app.register_blueprint(patchloyaltyb)
app.register_blueprint(deleteloyaltyb)
app.register_blueprint(healthcheckb)


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


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8050)

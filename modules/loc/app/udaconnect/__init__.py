########################################
# Location microservice for UdaConnect #
########################################

# Unnecessary comments are removed

# Person and PersonSchema are removed from import
# Connection and ConnectionSchema are removed
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema


def register_routes(api, app, root="api"):
    from app.udaconnect.controllers import api as udaconnect_api

    api.add_namespace(udaconnect_api, path=f"/{root}")

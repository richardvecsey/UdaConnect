####################################
# gRPC microservice for UdaConnect #
####################################

from app.udaconnect.models import Location, Person
from app.udaconnect.schemas import LocationSchema, PersonSchema


def register_routes(api, app, root="api"):
    from app.udaconnect.controllers import api as udaconnect_api

    api.add_namespace(udaconnect_api, path=f"/{root}")

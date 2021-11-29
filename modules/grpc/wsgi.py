####################################
# gRPC microservice for UdaConnect #
####################################

from concurrent import futures
import json
import logging
import time

from flask import Flask
import grpc

import location_pb2
import location_pb2_grpc
import person_pb2
import person_pb2_grpc

from app import db
from app.udaconnect.models import Location, Person
from geoalchemy2.functions import ST_Point
from app.config import config_by_name

keep_alive = True
insec_port = '[::]:5005'


class LocationsServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):

        request_data = {'person_id': request.person_id,
                        'creation_time': request.creation_time,
                        'latitude': request.latitude,
                        'longitude': request.longitude,}

        loc = location_pb2.LocationsMessage(**request_data)
        logger.info('Server got a protobuf `location` message {}'.format(loc))

        new_loc_obj = Location()
        new_loc_obj.person_id = loc.person_id
        new_loc_obj.creation_time = loc.creation_time
        new_loc_obj.coordinate = ST_Point(loc.latitude, loc.longitude)

        with app.app_context():
            db.session.add(new_loc_obj)
            db.session.commit()

        logger.info('Uploading into DB is complete.')

        return loc

class PersonsServicer(person_pb2_grpc.PersonServiceServicer):
    def Create(self, request, context):
        request_data = {'first_name': request.first_name,
                        'last_name': request.last_name,
                        'company_name': request.company_name,}

        person = person_pb2.PersonsMessage(**request_data)
        logger.info('Server got a protobuf `person` message {}'.format(person))

        new_person_obj = Person()
        new_person_obj.first_name = person.first_name
        new_person_obj.last_name = person.last_name
        new_person_obj.company_name = person.company_name

        with app.app_context():
            db.session.add(new_person_obj)
            db.session.commit()

        logger.info('Uploading into DB is complete.')

        return person


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('gRPC service for UdaConnect')

app = Flask(__name__)
app.config.from_object(config_by_name['prod'])
db.init_app(app)

grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationsServicer(), grpc_server)
person_pb2_grpc.add_PersonServiceServicer_to_server(PersonsServicer(), grpc_server)
grpc_server.add_insecure_port(insec_port)
grpc_server.start()
logger.info('gRPC service runs on port {}'.format(insec_port))

# Try to avoid thread failure with keep alive the thread.
# 86400 sec is a common valure for this parameter.
try:
    while keep_alive:
        time.sleep(86400)
except KeyboardInterrupt:
    grpc_server.stop(0)
    keep_alive = False

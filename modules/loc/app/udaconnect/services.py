########################################
# Location microservice for UdaConnect #
########################################

# Unnecessary imports are removed
# Unnecessary comments are removed
# PersonService and ConnectionService classes are removed

# Person and PersonSchemaare removed from import
# Connection and ConnectionSchema are removed

import logging
# from datetime import datetime, timedelta
from typing import Dict #List

from app import db
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from kafka import KafkaProducer
from sqlalchemy.sql import text


kafka_franz = 'udaconnect'
kafka_server = 'kafka.default.svc.cluster.local:9092'

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")
        try:
            kafka_maker.send(kafka_franz, json.dumps(location).encode())
            kafka_maker.flush()
            logger.info('Location created successfully.')
            # If reaching out Kafka with the new location data, we do not store
            # the location into our database. This is a cool feature, since
            # when an error occurs, we just pass the location data again without
            # worrying or handling database data duplications.
            new_location = Location()
            new_location.person_id = location["person_id"]
            new_location.creation_time = location["creation_time"]
            new_location.coordinate = ST_Point(location["latitude"],
                                               location["longitude"])
            db.session.add(new_location)
            db.session.commit()
            logger.info('Location stored successfully.')
        except KafkaTimeoutError:
            logger.error('Something went wrong. Timeout error occured during person creation process.')

        return new_location


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("Location service for UdaConnect")
kafka_maker = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

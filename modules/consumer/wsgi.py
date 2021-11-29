########################################
# Consumer microservice for UdaConnect #
########################################


import json
import logging

import grpc
from flask import Flask
from kafka import KafkaConsumer

import location_pb2
import location_pb2_grpc
import person_pb2
import person_pb2_grpc

from app import db
from app.config import config_by_name

kafka_franz = 'udaconnect'
kafka_server = 'kafka.default.svc.cluster.local:9092'
insec_channel = 'localhost:5005'

def locating(location):
    logger.info('Preparing `location` data to Kafka.')
    channel = grpc.insecure_channel(insec_channel)
    lstub = location_pb2_grpc.LocationServiceStub(channel)
    locations = location_pb2.LocationsMessage(
                person_id=location['person_id'],
                creation_time=location['creation_time'],
                lat=location['lat'],
                long=location['long'])
    lstub.Create(locations)
    logger.info('Sending `location` data to Kafka.')

def personating(person):
    logger.info('Preparing `person` data to Kafka.')
    channel = grpc.insecure_channel(insec_channel)
    pstub = person_pb2_grpc.PersonServiceStub(channel)
    persons = person_pb2.PersonsMessage(first_name = person['first_name'],
                                        last_name = person['last_name'],
                                        company_name = person['company_name'])
    pstub.Create(persons)
    logger.info('Sending `person` data to Kafka.')

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('Consumer service for UdaConnect')

app = Flask(__name__)
app.config.from_object(config_by_name['prod'])
db.init_app(app)

consumer = KafkaConsumer(kafka_franz, bootstrap_servers=[kafka_server])

for message in consumer:
    msg_data = json.loads((message.value.decode('utf-8')))

    if 'first_name' in msg_data and 'last_name' in msg_data:
        personating(msg_data)
    elif 'lat' in msg_data:
        locating(msg_data)
    elif 'long' in msg_data:
        locating(msg_data)
    else:
        logger.error('Failed to process the content of the message.')

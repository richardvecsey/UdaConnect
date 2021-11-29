####################################
# gRPC microservice for UdaConnect #
####################################
#            Test file             #
####################################

import grpc
import location_pb2
import location_pb2_grpc
import person_pb2
import person_pb2_grpc

insec_chennel = 'localhost:5005'

test_channel = grpc.insecure_channel(insec_chennel)
test_location_stub = location_pb2_grpc.LocationServiceStub(test_channel)
test_person_stub = person_pb2_grpc.PersonServiceStub(test_channel)

test_location = location_pb2.LocationsMessage(person_id=1,
                                              creation_time='21:15 hrs GMT+1',
                                              latitude='47.4979',
                                              longitude='19.0402')

test_person = person_pb2.PersonsMessage(id = 7,
                                        first_name = 'Richard',
                                        last_name = 'Vecsey',
                                        company_name = 'Udacity Student')

test_response = test_location_stub.Create(test_location)
test_response = test_person_stub.Create(test_person)

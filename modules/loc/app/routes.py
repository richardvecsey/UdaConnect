########################################
# Location microservice for UdaConnect #
########################################

# Unnecessary comments are removed

def register_routes(api, app, root="api"):
    from app.udaconnect import register_routes as attach_udaconnect

    attach_udaconnect(api, app)

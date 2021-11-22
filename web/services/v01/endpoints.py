from main import api

##############################
####### v0.1 imports #########
##############################

### debugging
from services.v01.debug.hello import Hello as Hello_v01

##############################
###### v0.1 resources ########
##############################

#debug
api.add_resource(Hello_v01, '/v01/hello', endpoint = 'Hello_v01')
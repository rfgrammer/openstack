import keystoneclient.v2_0.client as ksclient
# import keystoneauth1.v2_0.client as ksclient

# Replace the method arguments with the ones from your local config
keystone = ksclient.Client(auth_url="http://192.168.10.200:35357/v2.0",
                           username="admin",
                           password="1234",
                           tenant_name="admin")

# glance_service = keystone.services.create(name="glance",
#                             service_type="image",
#                             description="OpenStack Image Service")

for u in keystone.users.list():
    print(u)


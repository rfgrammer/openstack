import keystoneclient.v2_0.client as ksclient

# Replace the values below  the ones from your local config,
auth_url = "http://192.168.10.200:35357/v2.0"
username = "admin"
password = "1234"
tenant_name = "admin"

keystone = ksclient.Client(auth_url=auth_url, username=username,
                           password=password, tenant_name=tenant_name)

for u in keystone.users.list():
    print(u)

import os
import time
from novaclient import client as novaclient
from credentials import get_nova_creds

images = ['CentOS-7-x86_64-GenericCloud-1608', 'cirror', 'xenial-server-cloudimg-amd64-disk1']
flavors = ['server', 'desktop']
nics = [[{"net-id": "63c0b0ed-3983-4a10-bbc0-e6517d450490", "v4-fixed-ip": ''}],
        [{"net-id": "ff2f638f-f078-458e-9704-fe2f4a9f4665", "v4-fixed-ip": ''}]]
keys = ['cloudkey']


def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d


def create_nova_instance(nova, instance_name, image_name, flavor_name, key_name, nic):

    if nova.keypairs.findall(name=key_name):
        key = nova.keypairs.find(name=key_name)
    else:
        # with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
        #     nova.keypairs.create(name="mykey", public_key=fpubkey.read())
        print("No keypair found.")
        return

    image = nova.images.find(name=image_name)
    flavor = nova.flavors.find(name=flavor_name)
    instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, key_name=key_name, nics=nic)

    # Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)

        # Retrieve the instance again so the status field updates
        instance = nova.servers.get(instance.id)
        status = instance.status

    print "status: %s" % status
    attach_floating_IP(nova, instance_name)

    return status


def attach_floating_IP(nova, instance_name):
    fip = nova.floating_ips.list()
    print(fip)

    floating_ip = nova.floating_ips.create()
    instance = nova.servers.find(name=instance_name)
    instance.add_floating_ip(floating_ip)


def create_jenkins_server(nova):
    text_file = open("jenkins-tomcat.service", "r")
    lines = text_file.readlines()

    jenkins_post = ["sudo apt-get update",
                    "sudo apt-get install default-jdk",
                    "sudo groupadd tomcat",
                    "sudo useradd - s / bin / false - g tomcat - d / opt / tomcat tomcat",
                    "cd /tmp",
                    "curl -O http://apache.mirrors.ionfish.org/tomcat/tomcat-8/v8.5.5/bin/apache-tomcat-8.5.5.tar.gz",
                    "sudo mkdir /opt/tomcat",
                    "sudo tar xzvf apache-tomcat-8*tar.gz -C /opt/tomcat --strip-components=1",
                    "cd /opt/tomcat",
                    "sudo chgrp -R tomcat /opt/tomcat",
                    "sudo chmod -R g+r conf",
                    "sudo chmod g+x conf",
                    "sudo chown -R tomcat webapps/ work/ temp/ logs/",
                    "sudo update-java-alternatives -l",
                    "sudo touch /etc/systemd/system/tomcat.service",
                    "sudo echo " + lines + ">> /etc/systemd/system/tomcat.service"
                    "sudo systemctl daemon-reload",
                    "sudo systemctl start tomcat",
                    "sudo systemctl status tomcat",
                    "sudo ufw allow 8080",
                    "sudo ufw allow 22",
                    "sudo systemctl enable tomcat"]

    status = create_nova_instance(nova, "Jenkins", images[2], flavors[1], keys[0], nics[1])

    if status == "Active":
        for cmd in jenkins_post:
            os.system(cmd)


def main():
    creds = get_nova_creds()
    nova = novaclient.Client("2.0", **creds)

    # nic = [{"net-id": nova.networks.list()[0].id, "v4-fixed-ip": ''}]

    create_jenkins_server(nova)



if __name__ == "__main__":
    main()



#------------------------------
# TODO
#------------------------------
#
# cd / home / stack / images
# glance image-create --name xenial-server-cloudimg-amd64-disk1 --disk-format qcow2 --container-format bare --visibility public --progress < xenial-server-cloudimg-amd64-disk1.img
# glance image-create --name CentOS-7-x86_64-GenericCloud-1608 --disk-format qcow2 --container-format bare --visibility public --progress < CentOS-7-x86_64-GenericCloud-1608.qcow2c
# glance image-list
#
# #neutron router-delete router1
# #neutron net-delete public
# #neutron net-delete private
# #neutron net-list
# #neutron router-list
# #keystone user-password-update --pass iot*0371 admin
#
#
# # delete demo account
# # delete demo project
# # delete default public network
# # delete default private network
# # delete router1
# # create new public network
# # create new flavor : server
# # create new flavor : desktop
#
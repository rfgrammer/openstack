from novaclient import client as novaclient
from credentials import get_nova_creds
import os


def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d


def main():
    creds = get_nova_creds()
    nova = novaclient.Client("2.0", **creds)

    print(nova.servers.list())


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import boto3
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Get EC2 Hosts')
    parser.add_argument('hostname', nargs='?', help='(partial) hostname to filter on')
    return vars(parser.parse_args())

def interactive():
    args = parse_args()
    instances = get_hosts(args['hostname'])

    for instance in instances:
        print_inst_details(instance)


def print_inst_details(instance):
    for tag in instance['Tags']:
        if tag['Key'] == "Name":
            name = tag['Value']

    if 'PublicIpAddress' in instance:
        public_ip = instance['PublicIpAddress']
    else:
        public_ip = ""

    if 'PrivateIpAddress' in instance:
        private_ip = instance['PrivateIpAddress']
    else:
        private_ip = ""


    print("{0}{1} {2}{3}".format(name.ljust(30), instance['State']['Name'], private_ip.ljust(16), public_ip))
    # print instance


def get_hosts(hostname):
    client = boto3.client('ec2')

    if hostname is None:
        hostname = ""

    instances = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    "*{0}*".format(hostname),
                ]
            },
        ]
    )

    out_instances = []

    for reservation in instances['Reservations']:
        out_instances.extend(reservation['Instances'])

    return out_instances

if __name__ == "__main__":
    interactive()

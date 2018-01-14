import argparse
import os

from get_ec2_hosts import get_hosts, print_inst_details

SSH_COMMAND = 'autossh -M 0 -T -N -t'

ARG_PUBLIC_IP = 'P'
ARG_LOCAL_PORT = 'p'
ARG_REMOTE_PORT = 'r'
ARG_LIST = 'l'


def parse_args():
    parser = argparse.ArgumentParser(description='Get EC2 Hosts')
    parser.add_argument('hostname', help='(partial) hostname to connect to')
    parser.add_argument("-{0}".format(ARG_PUBLIC_IP), action='store_true',
                        help='connect to public IP address rather than private')
    parser.add_argument("-{0}".format(ARG_LOCAL_PORT), type=int, help='local port to start forwarding at')
    parser.add_argument("-{0}".format(ARG_REMOTE_PORT), type=int, help='remote port to forward to')
    parser.add_argument("-{0}".format(ARG_LIST), action='store_true', help='return list of matching hosts')
    return vars(parser.parse_args())


def sync_remotehome(instance, args):
    ip = get_ip(args, instance)

    cmd = "rsync -azL --exclude '*.swp' -e \"ssh\" ~/remotehome/ {0}:~/".format(ip)
    # print cmd
    os.system(cmd)


def get_ip(args, instance):
    if args[ARG_PUBLIC_IP]:
        if not 'PublicIpAddress' in instance:
            raise Exception("Public IP requested but instance doesn't have one")

        return instance['PublicIpAddress']
    else:
        return instance['PrivateIpAddress']


def connect_command(instance, args, offset):
    cmd = SSH_COMMAND

    base_port = args[ARG_LOCAL_PORT]
    remote_port = args[ARG_REMOTE_PORT]
    if base_port and remote_port:
        cmd = "{0} -L{1}:localhost:{2}".format(cmd, base_port + offset, remote_port)

    ip = get_ip(args, instance)
    cmd = "{0} {1}".format(cmd, ip)

    if offset != 0:
        cmd = "tmux split-window {0}".format(cmd)
    else:
        os.system("tmux select-layout tiled")

    cmd = "{0} \"~/bin/tmux attach || ~/bin/tmux new\"".format(cmd)

    # print cmd
    os.system(cmd)


def main():
    args = parse_args()

    instances = get_hosts(args['hostname'])

    if args['l']:
        for instance in instances:
            print_inst_details(instance)
        exit(0)

    i = len(instances)

    while i > 0:
        i -= 1
        sync_remotehome(instances[i], args)
        connect_command(instances[i], args, i)


main()

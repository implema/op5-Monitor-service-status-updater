#!/usr/bin/env python

'''A script to update the status of a service in op5 Monitor'''

# Author: Joel Rangsmo <jrangsmo@op5.com>

import argparse
import requests
import json

# Argument parsing
aparser = argparse.ArgumentParser(
    description='A script to update the status of a service in op5 Monitor')

aparser.add_argument('-M', '--monhost',
                     help='Specify op5 Monitor server', required=True)

aparser.add_argument('-u', '--username',
                     help='Specify op5 Monitor username', required=True)

aparser.add_argument('-p', '--password',
                     help='Specify op5 Monitor password', required=True)

aparser.add_argument('-H', '--host', help='Name of host object in op5 Monitor',
                     required=True)

aparser.add_argument('-S', '--service',
                     help='Description/name of service in op5 Monitor',
                     required=True)

aparser.add_argument('-s', '--status',
                     help='Status of service in op5 Monitor',
                     choices=('OK', 'WARNING', 'CRITICAL', 'UNKNOWN'),
                     required=True)

aparser.add_argument('-m', '--servicemsg',
                     help='Service status message', required=True)

aparser.add_argument('-i', '--insecure',
                     help='Disable SSL certificate verification',
                     action='store_false', default=True)

aparser.add_argument('-P', '--path',
                     help='Path to command in API',
                     default='/api/command/PROCESS_SERVICE_CHECK_RESULT')

args = aparser.parse_args()


# Setting status code depending on the value of args.status
if args.status == 'OK':
    statuscode = 0

elif args.status == 'WARNING':
    statuscode = 1

elif args.status == 'CRITICAL':
    statuscode = 2

elif args.status == 'UNKNOWN':
    statuscode = 3


# Service status update
try:
    update = requests.post('https://%s%s'
                           % (args.monhost, args.path),
                           verify=args.insecure,
                           timeout=15,
                           headers={'content-type': 'application/json'},
                           auth=(args.username, args.password),
                           data=json.dumps({"host_name": "%s" % args.host,
                                            "service_description": "%s"
                                            % args.service,
                                            "status_code": "%s" % statuscode,
                                            "plugin_output": "%s"
                                            % args.servicemsg
                                            }))

# Exception handling (timeouts, SSL issues, etc)
except requests.exceptions.Timeout:
    print('CRITICAL - Connection to host "%s" timed out'
          % args.monhost)

    exit(2)

except requests.exceptions.SSLError:
    print('CRITICAL - SSL Certificate validation error - ' +
          'use "--insecure" to disabled verification')

    exit(2)

except requests.exceptions.ConnectionError:
    print('CRITICAL - Failed to connect to host "%s"'
          % args.monhost)

    exit(2)

except requests.exceptions.RequestException as exception:
    print('UNKNOWN - Unexpected exception: "%s"'
          % exception)

    exit(3)


# Checks if the status update was successful
if update.status_code == 200:
    print('OK - Service "%s" on host "%s" was updated successfully'
          % (args.service, args.host))

    exit(0)

elif update.status_code == 400:
    print('CRITICAL - Host "%s" or service "%s" was not found. '
          % (args.service, args.host) +
          'Please check your spelling and capitilization')

    exit(2)

elif update.status_code == 401:
    print('CRITICAL - Username, password and/or ' +
          'the users priviliges was not accepted by server')

    exit(2)

elif update.status_code == 404:
    print('CRITICAL - The requested URL "%s" was not found'
          % args.path)

    exit(2)

else:
    print('UNKNOWN - Unexpected HTTP status code: "%s"'
          % update.status_code)

    exit(3)

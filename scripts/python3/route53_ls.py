#!/bin/python3

import sys
import boto3

from aws_library import Route53

if __name__ == "__main__":
    access_file = sys.argv[1]
    region_name = sys.argv[2]
    dns_name =  sys.argv[3] # "strangecraft.xyz"

    R53 = Route53(access_file, region_name)

    # Get the list of hosted zones
    hosted_zone_list = R53.listHostedZones( dns_name )
    [print(hz['Id']) for hz in hosted_zone_list]


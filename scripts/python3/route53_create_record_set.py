#!/bin/python3

import sys
import boto3
import json

from aws_library import Route53, ElasticLoadBalancer

if __name__ == "__main__":
    access_file = sys.argv[1]
    region_name = sys.argv[2]
    dns_name =  sys.argv[3] # "strangecraft.xyz"
    dns_prefix = sys.argv[4] 
    elb_arn = sys.argv[5] 

    R53 = Route53(access_file, region_name)
    ELB = ElasticLoadBalancer(access_file, region_name)

    # Get the list of hosted zones
    hz_list = R53.listHostedZones( dns_name )
    [print(hz['Id']) for hz in hz_list]

    # Get the list of DNS Names derived from the elb ARN
    elb_list = ELB.getElb( elb_arn )

    full_dns_name = f"{dns_prefix}.{dns_name}"
    for hz in hz_list:
        hosted_zone_id = hz['Id']
        r = R53.createRecordSets_Elb( hosted_zone_id, full_dns_name, elb_list, region_name )
        print(f"Hosted Zone Id: {hosted_zone_id}")
        print( json.dumps(r, indent=4, sort_keys=True, default=str) )




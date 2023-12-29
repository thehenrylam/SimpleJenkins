#!/bin/python3

import sys
import boto3

from aws_library import Route53

if __name__ == "__main__":
    access_file = sys.argv[1]
    region_name = sys.argv[2]
    dns_name =  sys.argv[3] # "strangecraft.xyz"
    dns_prefix = sys.argv[4] # "play"

    R53 = Route53(access_file, region_name)

    output = []
    # Get the list of hosted zones
    hosted_zone_list = R53.listHostedZones( dns_name )
    for hz in hosted_zone_list:
        # For each hosted zone, 
        #   use its Id to get its record sets (specified by the full domain name)
        #   delete the record sets
        hz_id = hz['Id']
        record_sets = R53.listRecordSets( hz_id, "A", f"{dns_prefix}.{dns_name}")
        removed_records = R53.removeRecordSets( hz_id, record_sets )
        output += removed_records
    [print(o) for o in output]


#!/bin/python3

import sys
import boto3
import re

from aws_library import ConvertTagsToFilter, ElasticComputeCloud, ElasticLoadBalancer

if __name__ == "__main__":
    access_file = sys.argv[1]
    region_name = sys.argv[2] # "us-east-1"
    vpc = sys.argv[3] # 'mcaws-beta'
    env = sys.argv[4] # 'prod'

    default_tags = [
        {'Key': 'project', 'Value': 'mcaws'},
        {'Key': 'vpc', 'Value': vpc}
    ]

    EC2 = ElasticComputeCloud( access_file, region_name )

    # Get a list of vpcs (so that we know for sure that we are working under the right VPC)
    filter_vpc_tags = ConvertTagsToFilter( default_tags )
    vpc_list = EC2.listVpcs( filter_vpc_tags )
    vpc_id_list = [ vpc['VpcId'] for vpc in vpc_list ]

    # Get a list of elbs that matches the given name pattern, vpc_list, and elb_tags
    elb_tags = default_tags + [ {'Key': 'env', 'Value': env} ]
    elb_name_pattern = r'.*' # For now, we'll allow all elb names and rely on vpc and tag filtering

    ELB = ElasticLoadBalancer( access_file, region_name )
    output = ELB.listElb( elb_name_pattern, vpc_id_list, elb_tags ) 
    [print(lb['LoadBalancerArn']) for lb in output]


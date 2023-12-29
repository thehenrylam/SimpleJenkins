#!/bin/python3

import sys
import boto3
import re

from aws_library import ConvertTagsToFilter, ConvertVpcsToFilter, ElasticComputeCloud, ElasticLoadBalancer

if __name__ == "__main__":
    access_file = sys.argv[1]
    region_name = sys.argv[2]
    vpc = sys.argv[3] # 'mcaws-beta'
    env = sys.argv[4] # 'prod'
    elb_protocol = sys.argv[5] # 'TCP_UDP'
    elb_port = int(sys.argv[6]) # 25565

    default_tags = [
        {'Key': 'project', 'Value': 'mcaws'},
        {'Key': 'vpc', 'Value': vpc}
    ]
    tag_environment = {'Key': 'env', 'Value': env}

    EC2 = ElasticComputeCloud( access_file, region_name )

    # Get a list of vpcs (so that we know for sure that we are working under the right VPC)
    filter_vpc_tags = ConvertTagsToFilter( default_tags )
    # vpc_list = EC2.listVpcs( default_tags )
    vpc_list = EC2.listVpcs( filter_vpc_tags )
    vpc_id_list = [ vpc['VpcId'] for vpc in vpc_list ]

    # Convert VPC ids into a filter 
    vpc_filters = ConvertVpcsToFilter( vpc_list )

    # Get a list of elbs that matches the given name pattern, vpc_id_list, and elb_tags
    tgt_tags = default_tags + [ {'Key': 'env', 'Value': env} ]
    tgt_name_pattern = r'.*' # For now, we'll allow all tgt names and rely on vpc and tag filtering

    ELB = ElasticLoadBalancer( access_file, region_name )

    # Get a list of target groups (to be used to create the load balancer)
    tgt_list = ELB.listTgt( tgt_name_pattern, vpc_id_list, tgt_tags )

    # Get a list of subnets (to be used to create the load balancer)
    sbn_tags = default_tags + [ tag_environment ]
    filter_sbn_tags = ConvertTagsToFilter( sbn_tags )
    sbn_list = EC2.listSubnets( filter_sbn_tags, vpc_filters )

    # Get a list of security groups (to be used to create the load balancer)
    scg_tags = default_tags + [ tag_environment, {'Key': 'purpose', 'Value': 'internet'} ] 
    filter_scg_tags = ConvertTagsToFilter( scg_tags )
    scg_list = EC2.listSecurityGroups( filter_scg_tags, vpc_filters )

    # Create the ELB (no listeners, yet)
    elb_name = f"{vpc}-elb-{env}-mc-proxy" 
    elb_tags = default_tags + [ tag_environment ]
    elb_list = ELB.createElb( elb_name, scg_list, sbn_list, elb_tags )

    # Add listeners into the ELB
    # elb_protocol = 'TCP_UDP'
    # elb_port = 25565
    elb_default_actions = [
        { 'Type': 'forward', 'TargetGroupArn': tgt['TargetGroupArn'] } for tgt in tgt_list
    ]
    
    for elb in elb_list:
        ELB.createElbListener(elb, elb_protocol, elb_port, elb_default_actions)
        print(elb["LoadBalancerArn"])

    pass


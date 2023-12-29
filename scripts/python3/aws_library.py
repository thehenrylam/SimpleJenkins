#!/bin/python3

import sys
import boto3
import re

def InitClient(client_type, access_file, region_name):
    # Client the client
    client = None

    with open(access_file, 'r') as file:
        # Read the first line (aws_access_key_id)
        aws_access_key_id = file.readline().strip()
        # Read the second line (aws_secret_access_key)
        aws_secret_access_key = file.readline().strip()
        
        # Initialize the ec2 client
        client = boto3.client(
            client_type,
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key,
            region_name = region_name
        )

    if client is None:
        err_msg = [
            f"{client_type} client is None.",
            f"access_file: {access_file}",
            f"region_name: {region_name}"
        ]
        raise Exception( "\n".join( err_msg ) )

    return client

def ConvertTagsToFilter(tag_list):
    # Convert the list of tags into a filter form
    filter_list = []
    for tag in tag_list:
        key = tag['Key']
        val = tag['Value']
        f = { 'Name': f"tag:{key}", 'Values': [ val ] }
        filter_list.append( f )
    return filter_list

def ConvertVpcsToFilter(vpc_list):
    # Convert the list of VPC ids into a filter form
    vpc_id_list = [ vpc['VpcId'] for vpc in vpc_list ]
    filter_list = [ { 'Name': 'vpc-id', 'Values': vpc_id_list } ]
    return filter_list


class Route53:
    def __init__(self, access_file, region_name):
        # Create the route53 client
        self.route53 = InitClient("route53", access_file, region_name)
        self.region_name = region_name
        return

    def listHostedZones(self, dns_name):
        # Get response from the list of hosted zones via the DNS name
        response = self.route53.list_hosted_zones_by_name( DNSName = dns_name )
        hz_list = response["HostedZones"]
        return hz_list

    def listRecordSets(self, hosted_zone_id, record_set_type, full_dns_name):
        # Safety settings (Disallow "SOA" and "NS" from being listed (to prevent it being deleted)
        if record_set_type in ["NS", "SOA"]:
            raise Exception("Unable to list record sets, record_set_type '{}' is invalid".format(record_set_type))

        # Set the record set name (Add a period at the end because AWS needs it)
        record_set_name = f"{full_dns_name}."

        # Get the current record set
        response = self.route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=record_set_name,
            StartRecordType=record_set_type
        )

        # Get the list of record sets and verify that it matches the complete URL
        output = []
        for record_set in response['ResourceRecordSets']:
            if record_set_name != record_set["Name"]:
                continue
            if record_set_type != record_set["Type"]:
                continue
            output.append( record_set )

        return output 

    def createRecordSets_Elb(self, hosted_zone_id, full_dns_name, elb_list, region_name):
        # From the list of elbs create a change list
        change_batch = { 'Changes': [] }

        full_record_name = f"{full_dns_name}"

        # Convert the list of elbs into changes in a change list
        for elb in elb_list:
            elb_dns_name = elb['DNSName']
            elb_hosted_zone = elb['CanonicalHostedZoneId']
            change = {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': full_record_name,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': elb_hosted_zone, 
                        'DNSName': elb_dns_name,
                        'EvaluateTargetHealth': False
                    }
                }
            }
            change_batch['Changes'].append( change )

        # return change_batch

        # Exit early if the change batch is empty
        if len(change_batch['Changes']) == 0:
            return None

        response = self.route53.change_resource_record_sets(
            HostedZoneId = hosted_zone_id,
            ChangeBatch = change_batch
        )
        return response

    def removeRecordSets(self, hosted_zone_id, record_sets):
        if len(record_sets) == 0:
            # If there are no record sets to remove, then exit early
            return []

        output = []

        # Aggregate the list of record sets into a change list
        change_list = []
        for rs in record_sets:
            change = {
                'Action': 'DELETE',
                'ResourceRecordSet': rs
            }
            change_list.append( change )
            output.append(rs["Name"]) # Add the record set name onto the output for log keeping

        # Update the record set in the hosted zone
        change_batch = { 'Changes': change_list }
        response = self.route53.change_resource_record_sets(
            HostedZoneId = hosted_zone_id,
            ChangeBatch = change_batch
        )

        return output


class ElasticComputeCloud:
    def __init__(self, access_file, region_name):
        # Create the ec2 client
        self.ec2 = InitClient("ec2", access_file, region_name)
        self.region_name = region_name
        return

    def listVpcs(self, tag_filters=None):
        list_of_filters = []
        list_of_filters += tag_filters if tag_filters is not None else []

        vpc_list = []

        # Aggregate all vpcs in a single list
        response = self.ec2.describe_vpcs(Filters=list_of_filters)
        vpc_list += response['Vpcs']
        while ( 'NextMarker' in response.keys() ):
            response = self.ec2.describe_vpcs(
                Filters=list_of_filters,
                Marker=response['NextMarker']
            )
            vpc_list += response['Vpcs']

        '''
        for vpc in vpc_list:
            vpc_id = vpc['VpcId']
            print(f"{vpc_id}")
        '''

        return vpc_list

    def listSubnets(self, tag_filters=None, vpc_filters=None):
        list_of_filters = []
        list_of_filters += tag_filters if tag_filters is not None else []
        list_of_filters += vpc_filters if vpc_filters is not None else []

        sbn_list = []

        # Aggregate all subnets in a single list
        response = self.ec2.describe_subnets(Filters=list_of_filters)
        sbn_list += response['Subnets']
        while ( 'NextMarker' in response.keys() ):
            response = self.ec2.describe_subnets(
                Filters=list_of_filters, 
                Marker=response['NextMarker']
            )
            sbn_list += response['Subnets']

        '''
        for sbn in sbn_list:
            sbn_arn = sbn['SubnetArn']
            sbn_vpc = sbn['VpcId']
            sbn_id = sbn['SubnetId']
            print(f"{sbn_vpc} : {sbn_id} : {sbn_arn}")
        '''

        return sbn_list

    def listSecurityGroups(self, tag_filters=None, vpc_filters=None):
        list_of_filters = []
        list_of_filters += tag_filters if tag_filters is not None else []
        list_of_filters += vpc_filters if vpc_filters is not None else []

        scg_list = []

        # Aggregate all security groups in a single list
        response = self.ec2.describe_security_groups(Filters=list_of_filters)
        scg_list += response['SecurityGroups']
        while ( 'NextMarker' in response.keys() ):
            response = self.ec2.describe_security_groups(
                    Filters=list_of_filters, 
                    Marker=response['NextMarker']
            )
            scg_list += response['SecurityGroups'] 

        '''
        for scg in scg_list:
            scg_name = scg['GroupName']
            scg_vpc = scg['VpcId']
            scg_id = scg['GroupId']
            print(f"{scg_vpc} : {scg_id} : {scg_name}")
        '''

        return scg_list

    def listInstances(self, tag_filters=None, vpc_filters=None, only_get_running=True):
        list_of_filters = []
        list_of_filters += tag_filters if tag_filters is not None else []
        list_of_filters += vpc_filters if vpc_filters is not None else []

        reservation_list = []
        # Aggregate all security groups in a single list
        response = self.ec2.describe_instances(Filters=list_of_filters)
        reservation_list += response['Reservations']
        while ( 'NextMarker' in response.keys() ):
            response = self.ec2.describe_security_groups(
                Filters=list_of_filters,
                Marker=response['NextMarker']
            )
            reservation_list += response['Reservations']

        eci_list = []
        for reservation in reservation_list:
            eci_list += reservation['Instances']

        output = []
        for eci in eci_list:
            instance_id = eci['InstanceId']
            instance_vpc = eci['VpcId']
            instance_sbn = eci['SubnetId']
            instance_ste = eci['State']
            # print(f"{instance_vpc} : {instance_sbn} : {instance_id} : {instance_ste}")
            if instance_ste['Name'] == 'running':
                output.append( eci )

        return output


class ElasticLoadBalancer:
    def __init__(self, access_file, region_name):
        # Clear the elbv2 client
        self.elbv2 = InitClient("elbv2", access_file, region_name)
        self.region_name = region_name
        return

    def filterElbName(self, lb_list, name_pattern):
        if name_pattern is None:
            return lb_list
        output = []
        for lb in lb_list:
            if re.search(name_pattern, lb['LoadBalancerName']):
                output.append( lb )
        return output

    def filterElbVpcs(self, lb_list, vpc_ids):
        if vpc_ids is None:
            return lb_list
        output = []
        for lb in lb_list:
            if lb['VpcId'] in vpc_ids:
                output.append( lb )
        return output

    def filterElbTags(self, lb_list, tags_to_filter):
        if tags_to_filter is None:
            return lb_list
        output = []
        for lb in lb_list:
            response = self.elbv2.describe_tags( ResourceArns=[ lb['LoadBalancerArn'] ] )
            lb_tags = response['TagDescriptions'][0]['Tags']
            if all(tag in lb_tags for tag in tags_to_filter):
                output.append( lb )
        return output

    def getElb(self, elb_arn):
        response = self.elbv2.describe_load_balancers( LoadBalancerArns=[elb_arn] )
        elb_list = response['LoadBalancers']
        return elb_list

    def listElb(self, name_filter_pattern=None, vpc_ids=None, tags_to_filter=None):
        # List all load balancers

        elb_list = []
        # Aggregate all load balancers in a single list
        response = self.elbv2.describe_load_balancers()
        elb_list += response['LoadBalancers']
        while ( 'NextMarker' in response.keys() ):
            response = self.elbv2.describe_load_balancers(Marker=response['NextMarker'] )
            elb_list += response['LoadBalancers']

        filtered_elb_list = elb_list
        filtered_elb_list = self.filterElbName(filtered_elb_list, name_filter_pattern)
        filtered_elb_list = self.filterElbVpcs(filtered_elb_list, vpc_ids)
        filtered_elb_list = self.filterElbTags(filtered_elb_list, tags_to_filter)

        '''
        # Extract and print load balancer details
        for load_balancer in filtered_elb_list:
            load_balancer_name = load_balancer['LoadBalancerName']
            load_balancer_arn = load_balancer['LoadBalancerArn']
            load_balancer_dns = load_balancer.get('DNSName', 'N/A')
            load_balancer_vpc = load_balancer['VpcId']
            dbg_msg = [
                " = {} = ".format( load_balancer_name ),
                "\tARN: {}".format( load_balancer_arn ),
                "\tDNS: {}".format( load_balancer_dns ),
                "\tVPC: {}".format( load_balancer_vpc )
            ]
            print( "\n".join(dbg_msg) )
        '''

        return filtered_elb_list

    def filterTgtName(self, tgt_list, name_pattern):
        if name_pattern is None:
            return tgt_list
        output = []
        for tgt in tgt_list:
            if re.search(name_pattern, tgt['TargetGroupName']):
                output.append( tgt )
        return output

    def filterTgtVpcs(self, tgt_list, vpc_ids):
        if vpc_ids is None:
            return tgt_list
        output = []
        for tgt in tgt_list:
            if tgt['VpcId'] in vpc_ids:
                output.append( tgt )
        return output

    def filterTgtTags(self, tgt_list, tags_to_filter):
        if tags_to_filter is None:
            return tgt_list
        output = []
        for tgt in tgt_list:
            response = self.elbv2.describe_tags( ResourceArns=[ tgt['TargetGroupArn'] ] )
            tgt_tags = response['TagDescriptions'][0]['Tags']
            if all(tag in tgt_tags for tag in tags_to_filter):
                output.append( tgt )
        return output

    def listTgt(self, name_filter_pattern=None, vpc_ids=None, tags_to_filter=None):
        tgt_list = []

        # Aggregate all target groups in a single list
        response = self.elbv2.describe_target_groups()
        tgt_list += response['TargetGroups']
        while ( 'NextMarker' in response.keys() ):
            response = self.elbv2.describe_target_groups(Marker=response['NextMarker'])
            tgt_list += response['TargetGroups']

        filtered_tgt_list = tgt_list
        filtered_tgt_list = self.filterTgtName(filtered_tgt_list, name_filter_pattern)
        filtered_tgt_list = self.filterTgtVpcs(filtered_tgt_list, vpc_ids)
        filtered_tgt_list = self.filterTgtTags(filtered_tgt_list, tags_to_filter)

        '''
        for target_group in filtered_tgt_list:
            target_group_name = target_group['TargetGroupName']
            target_group_arn = target_group['TargetGroupArn']
            target_group_vpc = target_group['VpcId']
            dbg_msg = [
                " = {} = ".format( target_group_name ),
                "\tARN: {}".format( target_group_arn ),
                "\tVPC: {}".format( target_group_vpc )
            ]
            print( "\n".join(dbg_msg) )
        '''

        return filtered_tgt_list

    def registerTgt_instances(self, tgt_arn, eci_list):
        if (len(eci_list) == 0):
            return

        # Convert the list of eci into a list of targets to register
        instance_targets = []
        for eci in eci_list:
            target = { 'Id': eci['InstanceId'] }
            instance_targets.append( target )

        response = self.elbv2.register_targets(
            TargetGroupArn = tgt_arn,
            Targets = instance_targets
        )

        return response

    def registerTgt_instances_ip(self, tgt_arn, eci_list):
        if (len(eci_list) == 0):
            return
        
        # Convert the list of eci into a list of targets to register (via IP)
        target_list = []
        for eci in eci_list:
            target = { 'Id': eci['PrivateIpAddress'] }
            target_list.append( target )

        response = self.elbv2.register_targets(
            TargetGroupArn = tgt_arn,
            Targets = target_list
        )
        
        return response

    def deregisterTgt(self, tgt_arn):
        # Describe the targets in the target group
        response = self.elbv2.describe_target_health(TargetGroupArn=tgt_arn)

        # Extract the target IDs
        target_ids = [target['Target']['Id'] for target in response['TargetHealthDescriptions']]

        if (len(target_ids) == 0):
            return {"Message": "No targets were found under the target group to remove"}

        response = self.elbv2.deregister_targets(
            TargetGroupArn=tgt_arn,
            Targets=[{'Id': target_id} for target_id in target_ids]
        )

        return response

    def createElb(self, elb_name, scg_list, sbn_list, tags):
        scg_id_list = [ scg['GroupId'] for scg in scg_list ]
        sbn_id_list = [ sbn['SubnetId'] for sbn in sbn_list ]

        # Create an ELB (network type)
        response = self.elbv2.create_load_balancer(
            Name = elb_name,
            Type = 'network',
            Subnets = sbn_id_list,
            Scheme = 'internet-facing',
            SecurityGroups = scg_id_list,
            Tags = tags
        )

        elb_list = response['LoadBalancers']

        return elb_list

    def createElbListener(self, elb, protocol, port, default_actions):
        # Create a listener within the ELB
        response = self.elbv2.create_listener(
            LoadBalancerArn = elb['LoadBalancerArn'],
            Protocol = protocol,
            Port = port,
            DefaultActions = default_actions
        )

        elb_listener_list = response['Listeners']
        return elb_listener_list

    def remove(self, elb_arn_list):
        for lb_arn in elb_arn_list:
            # Delete the load balancer
            self.elbv2.delete_load_balancer(LoadBalancerArn=lb_arn)
        return elb_arn_list 



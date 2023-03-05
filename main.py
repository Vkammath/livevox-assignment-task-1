import datetime

import boto3
import os
import sys
import json

aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']


def get_asg_describe(asgname):
    asg_client = boto3.client('autoscaling', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='ap-south-1')
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asgname])
    return asg_response

def get_ec2_details(instance_id):
    ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                              region_name='us-east-1')
    instance_details = ec2_client.describe_instances(InstanceIds=[instance_id])
    return instance_details


def main(argv):
    print(sys.argv)
    if len(sys.argv)>1:
        asg_response=get_asg_describe(str(sys.argv[1]))
        print(json.dumps(asg_response,indent=2,default=str))

        desired_count = asg_response["AutoScalingGroups"][0]["DesiredCapacity"]
        print("Desired count is "+str(desired_count))

        availability_zones,vpc_id,security_group,image_id,up_time = [],[],[],[],[]
        asg=asg_response['AutoScalingGroups'][0]

        for instance in asg['Instances']:
            instance_id = instance['InstanceId']
            instance_details = get_ec2_details(instance_id)
            print (instance_details)
            instance_details = instance_details['Reservations'][0]['Instances'][0]
            uptime = datetime.datetime.now(datetime.timezone.utc) - instance_details['LaunchTime']
            uptime_str = str(uptime).split('.')[0]
            up_time.append(uptime_str)
            print('Instance-ID: ' + instance_id)
            print('Security-Groups: ' + str(instance_details['SecurityGroups']))
            security_group.append(str(instance_details['SecurityGroups']))
            print('Uptime: ' + uptime_str)
            print('Availability-Zone: ' + instance_details['Placement']['AvailabilityZone'])
            availability_zones.append(instance_details['Placement']['AvailabilityZone'])
            print('VPC-ID: ' + instance_details['VpcId'])
            vpc_id.append(instance_details['VpcId'])
            print('Image-ID: ' + instance_details['ImageId'])
            image_id.append(instance_details['ImageId'])


        if desired_count == len(asg_response['AutoScalingGroups'][0]['Instances']) :
            print ("Desired count is equal to running instance count")
        else :
            print("Desired count is  not equal to running instance count")

        if len(asg_response['AutoScalingGroups'][0]['Instances']) == len(set(availability_zones)) :
            print("Running in different availability zones")
        else:
            print("Running in same availability zones")

        if len(set(image_id))== 1 :
            print("All instances are running with same image id")
        else:
            print("All instances are not running with same image id")

        if len(set(security_group)) == 1:
            print("All instances are running with same security group")
        else:
            print("All instances are not running with same security group")

        if len(set(vpc_id)) == 1:
            print("All instances are running with same vpc_id")
        else:
            print("All instances are not running with same vpc_id")

        print("uptime of running instances  : " +str(up_time))

    else:
        print("Please pass correct arguments")
        print("Usage ./sample-test.py asgname")

if __name__ == "__main__":
    main(sys.argv)

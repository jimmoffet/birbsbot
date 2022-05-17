#!/bin/bash

# Tutorial: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-fargate.html

# run these commands individually in the console via aws-cli

REGION=us-west-2
CLUSTER_NAME=tutorial
CLUSTER_CONFIG_NAME=tutorial
PROFILE_NAME=tutorial-profile
aws_access_key_id=
aws_secret_access_key=

# Create the Task Execution IAM Role

echo "Creating the task execution role:"
aws iam --region $REGION create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://task-execution-assume-role.json

echo "Attaching the task execution role policy:"
aws iam --region $REGION attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Define the AWS region to use, resource creation prefixes, and the cluster name to use with the Amazon ECS CLI
echo "Creating a cluster configuration:"
ecs-cli configure --cluster $CLUSTER_NAME --default-launch-type FARGATE --config-name $CLUSTER_CONFIG_NAME --region $REGION

echo "Creating a CLI profile using your access key and secret key:"
ecs-cli configure profile --access-key $aws_access_key_id --secret-key $aws_secret_access_key --profile-name $PROFILE_NAME

# Create a Cluster and Configure the Security Group

# Because you specified Fargate as your default launch type in the cluster configuration, 
# this command creates an empty cluster and a VPC configured with two public subnets.
echo "Create an Amazon ECS cluster with the ecs-cli up command:"
ecs-cli up --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME
# This command may take a few minutes to complete as your resources are created. 
# The output of this command contains the VPC and subnet IDs that are created.
# NOTE: The output of this command contains the VPC and subnet IDs that are created. Make note of them. (probably read them and echo in at EOF)

# NEED TO READ AND SET VPC_ID HERE

vpc_id=

echo "Retrieve the default security group ID for the VPC. Use the VPC ID from the previous output:"
aws ec2 describe-security-groups --filters Name=vpc-id,Values=$vpc_id --region $REGION

# The output of this command contains your security group ID, which is used in the next step.

security_group_id=

echo "Adding a security group rule to allow inbound access on port 80:"
aws ec2 authorize-security-group-ingress --group-id $security_group_id --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION

# NEED TO OBTAIN THE SUBNET IDS HERE AND SET THEM IN THE ECS-PARAMS FILE

# After you create the compose file, you can deploy it to your cluster with ecs-cli compose service up. By default, the command 
# looks for files called docker-compose.yml and ecs-params.yml in the current directory; you can specify a different docker compose 
# file with the --file option, and a different ECS Params file with the --ecs-params option. By default, the resources created by 
# this command have the current directory in their titles, but you can override that with the --project-name option. 
# The --create-log-groups option creates the CloudWatch log groups for the container logs.

echo "Deploy it to your cluster with ecs-cli compose service up. This will auto discover the docker-compose and ecs-params files in the current directory:"
ecs-cli compose --project-name $CLUSTER_NAME service up --create-log-groups --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME

echo "View the containers that are running in the service with ecs-cli compose service ps."
ecs-cli compose --project-name $CLUSTER_NAME service ps --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME

# Output should look like:
# Name                                                State    Ports                     TaskDefinition       Health
# $CLUSTER_NAME/$task_id/web  RUNNING  34.222.202.55:80->80/tcp  $CLUSTER_NAME:1      UNKNOWN

task_id=

echo "Displaying container logs"
ecs-cli logs --task-id $task_id --follow --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME
# The --follow option is similar to tail

echo "Scale instances to 2"
ecs-cli compose --project-name $CLUSTER_NAME service scale 2 --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME

echo "Run ps to view running containers"
ecs-cli compose --project-name tutorial service ps --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile tutorial-profile

echo "Scale instances to 1"
ecs-cli compose --project-name $CLUSTER_NAME service scale 2 --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME

#### CHECK THAT SERVER IS LIVE ON IP ADDRESS

# Clean up
echo "Deleting the service so that it stops the existing containers and does not try to run any more tasks."
ecs-cli compose --project-name $CLUSTER_NAME service down --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME

echo "Taking down the cluster, which cleans up the resources that we created earlier with ecs-cli up."
ecs-cli down --force --cluster-config $CLUSTER_CONFIG_NAME --ecs-profile $PROFILE_NAME
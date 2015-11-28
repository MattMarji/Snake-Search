import sys
import boto.ec2

def terminate(instance_id=None):

AWS_ACCESS_KEY_ID = 'xxxxxxxxxxxxxx'
AWS_ACCESS_KEY = 'xxxxxxxxxxxxxx'
EC2_REGION = 'us-east-1'

    # Check to determine if instance_id has been provided.
    if not instance_id:
        print "Oops, you're missing the instance_id..."
        return

    # Connect to instance
    conn = boto.ec2.connect_to_region(EC2_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY)

    # Terminate the instance(s) provided
    conn.terminate_instances(instance_ids=[instance_id])

    # Ensure instance is terminated...
    if (conn.get_all_instance_status(instance_ids=instance_id)== 'none'):
        print "Instance %s successfully terminated..." % instance_id
    else:
        print "Unable to find or terminate instance %s..." % instance_id

terminate('id-9d8f1149')

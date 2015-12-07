import boto.ec2


AWS_ACCESS_KEY_ID = 'xxxxxxxxxxxxxxx'
AWS_SECRET_ACCESS_KEY = 'xxxxxxxxxxxxx'
EC2_REGION = 'us-east-1'
KEYPAIR_NAME = 'ec2key'
KEYPAIR_SAVE_LOCATION = '.'
SEC_GROUP_NAME = 'csc326-group32'
SEC_GROUP_DESC = 'This group will allow users access to the Snake Search EC2 instance.'
IMAGE_ID = 'ami-8caa1ce4'
INSTANCE_TYPE = 't2.micro'

def deploy_ec2():
    # Establish a connection to us-east-1 instance
    conn = boto.ec2.connect_to_region(EC2_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Create a keypair, and save the .pem in the same dir as this file
    keypair = conn.create_key_pair(KEYPAIR_NAME)
    keypair.save(KEYPAIR_SAVE_LOCATION)

    # Create a security group
    sec_group = conn.create_security_group(SEC_GROUP_NAME, SEC_GROUP_DESC)

    # Apply necessary route changes to instance
    sec_group.authorize('icmp', -1, -1, '0.0.0.0/0')
    sec_group.authorize('tcp', 22, 22, '0.0.0.0/0')
    sec_group.authorize('tcp', 80, 80, '0.0.0.0/0')

    # create the instance
    res = conn.run_instances(image_id=IMAGE_ID, instance_type=INSTANCE_TYPE, key_name=KEYPAIR_NAME)

    # allocate an elastic ip (static) to the instance
    addr = conn.allocate_address()

    # Known instance id 'id-9d8f1149'
    addr.associate(instance_id=res.instances[0])

    # ... We are now ready to go. Return any necessary data.
    return addr, res.instances[0], KEYPAIR_SAVE_LOCATION+KEYPAIR_NAME+'.pem'

print deploy_ec2()

import boto.ec2

# Establish a connection to us-east-1 instance
conn = boto.ec2.connect_to_region('us-east-1',aws_access_key_id='AKIAJIXZSP44AQF465YQ', aws_secret_access_key='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')

# Create a keypair, and save the .pem in the same dir as this file
keypair = conn.create_key_pair('ec2key')
keypair.save('.')

# Create a security group
sec_group = conn.create_security_group('csc326-group32', 'This group will allow users access to the Snake Search EC2 instance.')

# Apply necessary route changes to instance
sec_group.authorize('icmp', -1, -1, '0.0.0.0/0')
sec_group.authorize('tcp', 22, 22, '0.0.0.0/0')
sec_group.authorize('tcp', 80, 80, '0.0.0.0/0')

# create the instance
res = conn.run_instances(image_id='ami-8caa1ce4', instance_type='t1.micro', key_name='ec2key')

# allocate an elastic ip (static) to the instance
#addr = conn.allocate_address()
#addr.associate(instance_id='id-9d8f1149')

# ... We are now ready to go!

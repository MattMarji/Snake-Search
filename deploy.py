import os
import sqlite3 as sql
import sys
import imp
import start_ec2

DATABASE = './snake_search.db'
URLS = './urls/urls.txt'

def deploy():

    print "Deploying: Removing old database..."
    os.system('rm -f %s' % DATABASE)

    print "Deploying: Connecting to new database..."
    db_conn = sql.connect(DATABASE)


    print "Deploying: Running crawler..."
    crawler = imp.load_source('crawler', 'crawler.py')
    crawl = crawler.crawler(db_conn, 'urls.txt')
    crawl.crawl(depth=1)

    print "Deploying: EC2 Instance ... this may take a while."
    # See start_ec2.py function: deploy_ec2() for details!
    ip_addr, instance_id, key_pair = start_ec2.deploy_ec2()

    print "Deploying: Transferring files to EC2 Instance ..."
    # Everything in this directory should be copied over.
    os.system('scp -r -o StrictHostKeyChecking=no -i %s ./ ubuntu@%s:~' % key_pair, ip_addr)

    print "Deploying: Starting Snake Search ..."

    # SSH, install pip with root access, install dependencies with root access, run Snake Search!!e
    os.system('ssh -i StrictHostKeyChecking=no -i %s ubuntu@%s sudo apt-get -y update && sudo apt-get -y install python-pip && sudo pip install beaker && sudo pip install boto && sudo pip install oauth2client && sudo pip install BeautifulSoup && sudo pip install google-api-python-client && sudo nohup python snake_search.py' % key_pair, ip_addr)

    print "Deploying: SUCCESSFULLY COMPLETED"
    print "Public IP: ", ip_addr
    print "Instance ID: ", instance_id

# We will assume that boto is NOT installed on target machine
def install_dependencies():
    os.system('git clone git://github.com/boto/boto.git')
    os.chdir('boto')

    # The user may be prompted to enter their password...
    os.system('python setup.py install --user')

    os.chdir('...')

    # Time to deploy the crawler, db, EC2 instance, and scp files!
    deploy()

# ENTRY POINT!
install_dependencies()

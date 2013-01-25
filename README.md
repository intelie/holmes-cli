holmes-admin
=============

IEM administration interface

- Run `./holmes-admin -h` to see usage options
- Before running, edit the configuration file `conf/holmes_admin_conf.py`

It is recommended to use python-ldap 2.3.13 due to this problem:
http://stackoverflow.com/questions/6475118/python-ldap-os-x-10-6-and-python-2-6

# Installation: 
- sudo apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev
- pip install -r requirements.txt

# Item Catalog Project

An application that provides a list of items within a variety of categories.

## Server Information
IP address: 52.207.224.204  
SSH port: 2200

## URL of Web Application
http://52.207.224.204/

## Software Installation and Configuration
- Created an Ubuntu Linux server instance on Amazon Lightsail
- Updated all currently installed packages
- Changed the SSH port from 22 to 2200
- Created a new user account named grader
- Gave grader the permission to sudo
- Enforced grader to login using key based authentication
- Disabled remote login for root user
- Installed and configured Apache to serve a Python mod_wsgi application
- Installed and configured PostgreSQL
- Installed Git
- Cloned and setup Item Catalog project from Github repository
- Configured .git directory to not be publicly accessible via a browser

## Resources
[OpenSSH Quick Reference]

## SSH key location for grader
/home/grader/.ssh/authorized_keys  
passphrase: grader  



[OpenSSH Quick Reference]: <http://www.cheat-sheets.org/saved-copy/OpenSSH_quickref.pdf>
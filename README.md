ServiceMappingLab

A complete VirtualBox lab to explore and test the ServiceNow Service Mapping module, using a simulated application environment with:

HAProxy Load Balancer

Two Flask Web Servers

PostgreSQL Database

All running on Ubuntu Server VMs inside VirtualBox.

This repository contains all scripts and configuration files needed to set up the lab quickly.

📌 Overview

This lab creates a realistic environment that ServiceNow Service Mapping can discover:

           ┌──────────────────┐
           │   Load Balancer  │  (HAProxy)
           │ 192.168.2.119    │
           └───────┬──────────┘
                   │
     ┌─────────────┴─────────────┐
     │                           │
┌──────────────┐         ┌────────────────┐
│   APP01      │         │     APP02      │
│ Flask + DB   │         │ Flask Only     │
│ 192.168.2.120│         │ 192.168.2.121  │
└──────────────┘         └────────────────┘


Each VM is based on a single template, cloned to speed up creation.

🖥 Requirements

Windows with VirtualBox

Ubuntu Server ISO (ubuntu-22.04 or ubuntu-24.04)

PowerShell (for scp)

Local network with DHCP (recommended)

1️⃣ Create the Base VM (Template)

Open VirtualBox → New

Settings:

Name: labtemplate

OS: Ubuntu (64-bit)

RAM: 2048–4096 MB

CPU: 2–4 cores

Disk: 25 GB (VDI, dynamic)

Network:

Adapter 1 → Bridged Adapter

Check Cable Connected

Mount the Ubuntu ISO:

Settings → Storage → Empty → Choose a disk file.

Start the VM and complete installation.

2️⃣ Ubuntu Installation Notes

During Ubuntu Server installation:

✔ Select Ubuntu Server (NOT minimized)
✔ Create the user:

Username: lab  
Password: your_choice


✔ Enable OpenSSH Server
✔ Skip optional snaps
✔ Reboot and log in

3️⃣ Configure Static Network (Netplan)

Each VM will need a different IP later — configure the template with any static IP or leave DHCP for now.

Check the interface:

ip a


Edit netplan:

sudo nano /etc/netplan/50-cloud-init.yaml


Example:

network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 192.168.2.119/24
      gateway4: 192.168.2.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4


Apply:

sudo netplan apply

4️⃣ Prepare the Template for Cloning

Inside the VM, run:

sudo rm -f /etc/machine-id
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id


Shutdown the VM:

sudo shutdown -h now

5️⃣ Clone the Template VM

Create 3 clones:

Clone Name	Purpose	Example IP
loadbalance	HAProxy	192.168.2.119
app01	Flask + PostgreSQL	192.168.2.120
app02	Flask only	192.168.2.121

Clone settings:

Right-click VM → Clone

Select: Full Clone

Enable: Reinitialize MAC Address

⚠ REQUIRED for networking to work.

6️⃣ Configure Netplan on Each Clone

Edit on each VM:

sudo nano /etc/netplan/50-cloud-init.yaml


Set a unique IP.

Example for APP01:

addresses:
  - 192.168.2.120/24


Apply:

sudo netplan apply


Verify:

ifconfig

7️⃣ Copy Lab Files from Windows to VM Using SCP

From PowerShell:

scp .\setup.py lab@192.168.2.120:/home/lab/
scp .\app_flask.py lab@192.168.2.120:/home/lab/
scp .\app_flask.py lab@192.168.2.121:/home/lab/
scp .\haproxy.cfg lab@192.168.2.119:/home/lab/
scp .\requirements.txt lab@<vm-ip>:/home/lab/


⚠ If connection fails:

sudo systemctl restart ssh

8️⃣ Update HAProxy Config

Edit haproxy.cfg with your actual VM IPs:

backend flask_servers
    balance roundrobin
    server app01 192.168.2.120:5000 check
    server app02 192.168.2.121:5000 check


You may edit on Windows before copying or directly inside Linux:

nano haproxy.cfg

9️⃣ Run the Setup Script on Each VM

Inside each VM:

chmod +x setup.py
sudo python3 setup.py


Select role:

1 - Load Balancer (HAProxy)
2 - APP1 (Flask + PostgreSQL)
3 - APP2 (Flask only)

About Python requirements

Ubuntu 24 blocks system-wide pip installs.

The included requirements.txt already contains:

--break-system-packages
Flask==3.0.0
psycopg2-binary


This allows installation without a virtual environment.

🔟 PostgreSQL Notes

The script attempts database creation, but depending on version you may need to run manually:

sudo -u postgres psql


Inside psql:

CREATE DATABASE labdb;
CREATE USER lab WITH ENCRYPTED PASSWORD 'lab123';
GRANT ALL PRIVILEGES ON DATABASE labdb TO lab;


Your Flask table creation code will run automatically on first execution.

1️⃣1️⃣ Check Services
Flask
sudo systemctl status flask

HAProxy
sudo systemctl status haproxy


Restart:

sudo systemctl restart flask
sudo systemctl restart haproxy

✔ Testing the Lab
APP Servers
http://192.168.2.120:5000
http://192.168.2.121:5000

Load Balancer
http://192.168.2.119:5000


Refreshing the LB endpoint should alternate between app01 → app02.

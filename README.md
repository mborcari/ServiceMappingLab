ServiceMappingLab

A complete VirtualBox-based lab designed to explore and test the ServiceNow Service Mapping module using a simple multi-tier application environment.

<div align="center">
🧩 Components Included
Component	Description
🔀 HAProxy	Load Balancer (HTTP round-robin)
🧪 APP01	Flask App + PostgreSQL Database
🌐 APP02	Flask App only
🐧 Ubuntu Server	All VMs run on Ubuntu Server
</div>
✨ Overview

This lab simulates a realistic environment that ServiceNow Discovery can map and analyze.
```text
                         +----------------------+
                         |     Load Balancer    |
                         |        HAProxy       |
                         |     192.168.2.119    |
                         +-----------+----------+
                                     |
             -------------------------------------------------
             |                                               |
  +-----------------------+                     +-----------------------+
  |        APP01          |                     |        APP02          |
  |   Flask + PostgreSQL  |                     |       Flask Only      |
  |     192.168.2.120     |                     |     192.168.2.121     |
  +-----------------------+                     +-----------------------+
```


Each VM is created from a single template and cloned for fast setup.

📦 Requirements

Windows 10 or 11

Oracle VirtualBox

Ubuntu Server ISO (22.04 / 24.04 recommended)

PowerShell (for SCP transfers)

Local network with DHCP or static addressing

Basic Linux knowledge

🚀 1. Create the Base Template VM
🔧 VirtualBox Settings
Setting	Value
OS	Ubuntu (64-bit)
RAM	2–4 GB
CPU	2–4 cores
Disk	25 GB (dynamic VDI)
Network	Bridged Adapter
Cable Connected	✔ Enable
🐧 Ubuntu Installation

During installation:

✔ Select Ubuntu Server
✔ Enable OpenSSH Server
✔ Create user:

Username: lab
Password: <your-password>


✔ Reboot the VM
✔ Verify SSH running:

systemctl status ssh

🌐 2. Configure Networking (Netplan)

Check interface name:

ip a


Edit configuration:

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


Apply settings:

sudo netplan apply

🧼 3. Prepare VM for Cloning

Ensure unique machine IDs for each clone:

sudo rm -f /etc/machine-id
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
sudo shutdown -h now

🧬 4. Clone the Template (Important)

Clone three VMs:

VM	Role	Example IP
loadbalance	HAProxy	192.168.2.119
app01	Flask + PostgreSQL	192.168.2.120
app02	Flask only	192.168.2.121

Clone with:

✔ Full Clone
✔ Reinitialize MAC Address
✔ Network = Bridged Adapter

Repeat netplan config for each VM.

📁 5. Transfer Lab Files (PowerShell SCP)

Example:

scp .\setup.py lab@192.168.2.120:/home/lab/
scp .\requirements.txt lab@192.168.2.120:/home/lab/
scp .\haproxy.cfg lab@192.168.2.119:/home/lab/


If SSH fails:

sudo systemctl restart ssh

⚙️ 6. Configure HAProxy

Edit configuration:

sudo nano haproxy.cfg


Example backend:

backend flask_servers
    balance roundrobin
    server app1 192.168.2.120:5000 check
    server app2 192.168.2.121:5000 check


Apply:

sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg
sudo systemctl restart haproxy

🧰 7. Run the Setup Script

Make executable:

chmod +x setup.py


Execute:

sudo python3 setup.py


Choose VM role:

1 - Load Balancer
2 - APP1 (Flask + PostgreSQL)
3 - APP2 (Flask only)


The script will:

✔ Install Python packages
✔ Install system dependencies
✔ Configure systemd services
✔ Start Flask automatically
✔ Setup PostgreSQL (APP01)

🗃️ 8. PostgreSQL Manual Fix (If Needed)

If DB creation fails:

sudo -u postgres psql


Run:

CREATE DATABASE labdb;
CREATE USER lab WITH ENCRYPTED PASSWORD 'lab123';
GRANT ALL PRIVILEGES ON DATABASE labdb TO lab;


Exit:

\q

🔍 9. Validate Services
Flask
sudo systemctl status flask

PostgreSQL
sudo systemctl status postgresql

HAProxy
sudo systemctl status haproxy


Restart all:

sudo systemctl restart flask
sudo systemctl restart haproxy
sudo systemctl restart postgresql

🌐 10. Test the Lab
APP Servers
http://192.168.2.120:5000
http://192.168.2.121:5000

Load Balancer (Round Robin)
http://192.168.2.119:5000

🎉 Ready for ServiceNow Discovery

You can now:

✔ Run Discovery
✔ Build Application Services
✔ Validate TCP connections
✔ Observe LB relationships
✔ Practice Mapping and Troubleshooting

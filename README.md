# ServiceMappingLab

A complete VirtualBox lab to explore and test the ServiceNow Service Mapping module, using a simulated multi-tier application:

- HAProxy Load Balancer  
- Two Flask Web Servers  
- PostgreSQL Database  
- All running on Ubuntu Server VMs  

---

## 🧭 Overview

This lab simulates a realistic environment that ServiceNow Discovery can analyze.

```
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

Each VM is cloned from a single template to speed up deployment.

---

## 📦 Requirements

- Windows 10 or 11 with 32gb RAM and good processor!
- Oracle VirtualBox
- Ubuntu Server ISO (22.04 or 24.04 recommended)
- PowerShell (for SCP transfers)
- DHCP or static network
- Basic Linux knowledge

---

## 🛠️ 1. Creating the Template VM

1. Open **VirtualBox → New**
2. Select:
   - Ubuntu (64-bit)
   - 2 GB RAM
   - 32 GB disk (VDI)
3. Boot the Ubuntu ISO and install Ubuntu Server

During installation enable:

```
✔ OpenSSH Server
```

After installation:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo shutdown now
```

---

## 🧬 2. Cloning the Template

Right-click the template → **Clone**

```
✔ Full Clone
✔ Reinitialize MAC Address
```

Create:

| VM  | Role | Example IP |
|-----|------|------------|
| LB | Load Balancer | 192.168.2.119 |
| APP01 | Flask + PostgreSQL | 192.168.2.120 |
| APP02 | Flask Only | 192.168.2.121 |

VirtualBox Network Adapter:

```
Bridged Adapter
Cable Connected = ON
```

---

## 🌐 3. Configuring Static IPs (Netplan)

Edit:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Example:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 192.168.2.120/24
      gateway4: 192.168.2.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Apply:

```bash
sudo netplan apply
```

If interface goes down:

```bash
sudo ip link set enp0s3 down
sudo ip link set enp0s3 up
```

---

## 🔁 4. Copying Files using SCP (PowerShell)

From Windows:

```powershell
scp .\setup.py lab@192.168.2.120:/home/lab/
scp .\haproxy.cfg lab@192.168.2.119:/home/lab/
scp .\app_flask.py lab@192.168.2.120:/home/lab/
scp .\app_flask.py lab@192.168.2.121:/home/lab/
```

If SSH fails:

```bash
sudo ufw allow ssh
```

---

## ⚙️ 5. Running the Setup Script

Make executable:

```bash
chmod +x setup.py
```

Execute:

```bash
sudo python3 setup.py
```

You will see:

```
[1] Load Balancer (HAProxy)
[2] APP01 (Flask + PostgreSQL)
[3] APP02 (Flask Only)
```

---

## 🐍 6. Installing Python Requirements

Because Ubuntu uses externally-managed Python:

```bash
pip3 install -r requirements.txt --break-system-packages
```

`requirements.txt` example:

```
Flask==3.0.0
psycopg2-binary
```

---

## 🐘 7. Configuring PostgreSQL (APP01 Only)

Install:

```bash
sudo apt install -y postgresql postgresql-contrib
```

Create DB and user:

```bash
sudo -u postgres psql -c "
CREATE DATABASE labdb;
CREATE USER lab WITH ENCRYPTED PASSWORD 'lab123';
GRANT ALL PRIVILEGES ON DATABASE labdb TO lab;
"
```

Validate:

```bash
sudo -u postgres psql -l
```

---

## 🔥 8. Running Flask as a System Service

Create service file:

```bash
sudo nano /etc/systemd/system/flask.service
```

Paste:

```ini
[Unit]
Description=Flask App
After=network.target

[Service]
User=lab
WorkingDirectory=/home/lab
ExecStart=/usr/bin/python3 /home/lab/app_flask.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask
sudo systemctl start flask
sudo systemctl status flask
```

---

## 🌀 9. HAProxy Setup (LB VM)

Edit:

```bash
sudo nano /etc/haproxy/haproxy.cfg
```

Example config:

```cfg
frontend http_front
    bind *:80
    mode http
    default_backend app_servers

backend app_servers
    mode http
    balance roundrobin
    server app01 192.168.2.120:5000 check
    server app02 192.168.2.121:5000 check
```

Restart:

```bash
sudo systemctl restart haproxy
```

Test:

```bash
curl http://192.168.2.119
```

---

## 🚀 10. Ready for ServiceNow Testing

You can now run:

- Discovery
- Traffic-Based Mapping
- Service Mapping Patterns

The environment behaves like a real multi-tier service.

---

## 🎯 Done!

Your lab is ready for use.  
Happy Mapping!

# ServiceMappingLab

A fully self-contained VirtualBox lab designed to simulate a small multi-tier application for **ServiceNow Discovery** and **Service Mapping**.

This repository contains **all required files**, including:

- `setup.py` (automated VM configuration tool)  
- `haproxy.cfg` (load balancer configuration)  
- `app_flask.py` & `app_flask_db.py` (Flask apps with/without PostgreSQL)  
- `requirements.txt`  
- Systemd service templates  

Everything is ready — **you only need to copy the files into each VM and run the setup script.**

---

## 🧭 Overview

This lab provides a realistic environment with:

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

---

# ⚙️ 1. VirtualBox Setup

## 1.1 Create the Template VM

1. Open VirtualBox → **New**
2. Configure:
   - Name: `labtemplate`
   - OS: Ubuntu (64-bit)
   - RAM: **2 GB**
   - CPU: **2 cores**
   - Disk: **32 GB (VDI, dynamically allocated)**

3. Boot the Ubuntu Server ISO (22.04 or 24.04 recommended)

During installation:

```
✔ Enable OpenSSH Server
✔ Use entire disk (guided)
✔ Hostname: labtemplate
✔ Username: lab
✔ Password: your choice
```

After installation:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo shutdown now
```

Your template VM is now ready.

---

# ⚙️ 2. Cloning VMs From Template

You will create 3 clones:

| VM Name | Role | IP Address |
|--------|------|------------|
| ServiceNowLB | HAProxy Load Balancer | 192.168.2.119 |
| ServiceNowAPP01 | Flask + PostgreSQL | 192.168.2.120 |
| ServiceNowAPP02 | Flask Only | 192.168.2.121 |

### Clone procedure (very important)

Right-click `labtemplate`:

```
Clone → Full Clone → Reinitialize MAC Address → Continue
```

Repeat for each of the 3 VMs.

---

# 🌐 3. Configure VirtualBox Networking

Each VM:

```
Settings → Network → Adapter 1:
✔ Bridged Adapter
✔ Cable Connected
Promiscuous Mode: Allow All
```

### Important Notes
- If cloning breaks the network, click **Refresh MAC** before booting.
- If VM shows **DOWN** state on ethernet interface, restart link:

```bash
sudo ip link set enp0s3 down
sudo ip link set enp0s3 up
```

---

# 🌐 4. Configure Static IPs (Netplan)

Each VM must have a unique static IP.

Edit Netplan:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Example (APP01):

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

Check:

```bash
ip a
ping 8.8.8.8
```

---

# 📂 5. Copying Files Into VMs (Using PowerShell SCP)

Navigate to the repo folder:

```powershell
cd C:\ServiceMappingLab
```

Copy files to each VM:

### Example for APP01:

```powershell
scp .\* lab@192.168.2.120:/home/lab/
```

### Example for APP02:

```powershell
scp .\* lab@192.168.2.121:/home/lab/
```

### Example for LB:

```powershell
scp .\haproxy.cfg lab@192.168.2.119:/home/lab/
```

If SSH fails:

```bash
sudo ufw allow ssh
```

---

# 🧰 6. Running the Automated Setup Script

Inside each VM:

```bash
chmod +x setup.py
sudo python3 setup.py
```

You will see:

```
[1] Load Balancer (HAProxy)
[2] APP1 (Flask + PostgreSQL)
[3] APP2 (Flask Only)
```

Choose according to the VM role.

---

# 🐘 7. PostgreSQL Setup (APP01 Only)

The `setup.py` script installs PostgreSQL automatically.

If database creation fails (Ubuntu sometimes blocks DB creation inside transaction), run manually:

```bash
sudo -u postgres psql
```

Inside PostgreSQL console:

```sql
CREATE DATABASE labdb;
CREATE USER lab WITH ENCRYPTED PASSWORD 'lab123';
GRANT ALL PRIVILEGES ON DATABASE labdb TO lab;
\q
```

Validate:

```bash
sudo -u postgres psql -l
```

---

# 🔥 8. Flask Application Service

The setup script creates:

```
/etc/systemd/system/flask.service
```

To check service status:

```bash
sudo systemctl status flask
```

Start manually:

```bash
sudo systemctl start flask
```

Enable on boot:

```bash
sudo systemctl enable flask
```

Test locally:

```bash
curl http://127.0.0.1:5000
```

---

# 🔀 9. HAProxy Configuration (Load Balancer)

File location:

```
/etc/haproxy/haproxy.cfg
```

Example included in the repository:

```cfg
frontend http_front
    bind *:80
    default_backend app_servers

backend app_servers
    balance roundrobin
    server app01 192.168.2.120:5000 check
    server app02 192.168.2.121:5000 check
```

Restart service:

```bash
sudo systemctl restart haproxy
```

Check status:

```bash
sudo systemctl status haproxy
```

Test from LB:

```bash
curl http://192.168.2.119
```

---

# ✔️ 10. Final Validation Checklist

### Load Balancer
- `curl http://192.168.2.119` returns alternating APP responses.

### APP01 (with DB)
```bash
curl http://192.168.2.120
sudo systemctl status flask
sudo -u postgres psql -l
```

### APP02 (without DB)
```bash
curl http://192.168.2.121
sudo systemctl status flask
```

### ServiceNow Discovery
- Use **SSH credentials**
- Test Connectivity to each IP
- Run **Horizontal Discovery**
- Run **Traffic-Based Discovery**
- Run **Service Mapping**

---

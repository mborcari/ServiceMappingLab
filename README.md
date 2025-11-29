# ServiceMappingLab

A fully self-contained VirtualBox lab designed to simulate a small multi-tier application for **ServiceNow Discovery** and **Service Mapping**.

This repository includes all files required to configure 3 VMs:

- **HAProxy Load Balancer**
- **Flask Web Server + PostgreSQL**
- **Flask Web Server (no DB)**

All configuration scripts, Python apps, HAProxy config, and systemd service files are provided.

---

# 🧭 Overview

This lab emulates a realistic service with dependencies for Service Mapping:

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

APP01 and APP02 serve as web nodes. HAProxy balances them.  
APP01 contains PostgreSQL to simulate database dependencies.

---

# ⚙️ 1. VirtualBox Setup

## 1.1 Create the Template VM

1. Open **VirtualBox → New**
2. Configure:
   - OS: Ubuntu (64-bit)
   - RAM: **2 GB**
   - CPU: **2 cores**
   - Disk: **32 GB VDI**
3. Boot from **Ubuntu Server ISO (22.04 or 24.04 recommended)**

During installation enable:
```
✔ OpenSSH Server
```

After installation:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo shutdown now
```

This VM is your **template**.

---

# 📂 2. Copy Repository Files Into the Template (IMPORTANT)

Before cloning, copy all files from this GitHub repo into **/home/lab** of the template VM.

### From Windows PowerShell:

```powershell
cd C:\ServiceMappingLab
scp .\* lab@<TEMPLATE_IP>:/home/lab/
```

Example:

```powershell
scp .\* lab@192.168.2.150:/home/lab/
```

### Inside the VM verify:

```bash
ls -l /home/lab
```

You should see ALL files:

```
setup.py
haproxy.cfg
app_flask.py
app_flask_db.py
requirements.txt
flask.service
run_flask.sh
```

### Shut down template:

```bash
sudo shutdown now
```

**Only after this step you can clone.**

---

# 🧬 3. Create Clones

Create 3 clones from the template:

| VM Name | Role | IP Address |
|--------|------|------------|
| ServiceNowLB | Load Balancer | 192.168.2.119 |
| ServiceNowAPP01 | Flask + PostgreSQL | 192.168.2.120 |
| ServiceNowAPP02 | Flask Only | 192.168.2.121 |

Clone procedure:

```
Right-click VM → Clone → Full Clone → Reinitialize MAC Address
```

Repeat for all 3.

---

# 🌐 4. VirtualBox Network Configuration

Each clone must use:

```
Settings → Network → Adapter 1:
✔ Bridged Adapter
✔ Cable Connected
Promiscuous Mode: Allow All
```

If interface fails to start:

```bash
sudo ip link set enp0s3 down
sudo ip link set enp0s3 up
```

---

# 🌐 5. Configure Static IPs (Netplan)

Open Netplan config:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Example for APP01:

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

Validate:

```bash
ip a
ping 8.8.8.8
```

---

# 🔁 6. Running the Setup Script

Make executable:

```bash
chmod +x setup.py
```

Run:

```bash
sudo python3 setup.py
```

You will be prompted:

```
[1] Configure Load Balancer (HAProxy)
[2] Configure APP01 (Flask + PostgreSQL)
[3] Configure APP02 (Flask Only)
```

Choose according to the VM's role.

---

# 🐍 7. Install Python Requirements

Ubuntu uses externally-managed Python, so install with:

```bash
pip3 install -r requirements.txt --break-system-packages
```

requirements.txt includes:

```
Flask==3.0.0
psycopg2-binary
```

---

# 🐘 8. PostgreSQL Setup (APP01 Only)

The setup script installs PostgreSQL.

If manual DB initialization is required:

```bash
sudo -u postgres psql
```

Inside psql:

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

# 🔥 9. Flask Application Service

The setup script configures this service:

```
/etc/systemd/system/flask.service
```

Start:

```bash
sudo systemctl start flask
```

Enable:

```bash
sudo systemctl enable flask
```

Status:

```bash
sudo systemctl status flask
```

Test:

```bash
curl http://127.0.0.1:5000
```

---

# 🔀 10. Configure HAProxy (Load Balancer)

File:

```bash
sudo nano /etc/haproxy/haproxy.cfg
```

Example configuration:

```cfg
frontend http_front
    bind *:80
    default_backend app_servers

backend app_servers
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

Should alternate responses between APP01 and APP02.

---

# ✔️ 11. Validation Checklist

### Load Balancer
```bash
curl http://192.168.2.119
sudo systemctl status haproxy
```

### APP01
```bash
curl http://192.168.2.120
sudo systemctl status flask
sudo -u postgres psql -l
```

### APP02
```bash
curl http://192.168.2.121
sudo systemctl status flask
```

---

# 🚀 12. Ready for ServiceNow Discovery & Mapping

You may now:

- Create SSH credentials  
- Test connectivity  
- Run Discovery  
- Perform Traffic-Based Mapping  
- Build ASMs (Application Service Maps)  
- Validate relationships (LB → Apps → DB)  

This environment works exactly like a small on-premise datacenter.

---

# 🤝 Contributions

Feel free to fork, improve or submit pull requests.

---

# 🎉 Enjoy Your Lab

This project provides everything needed for a complete end-to-end ServiceNow Service Mapping learning experience.


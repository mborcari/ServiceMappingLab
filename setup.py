#!/usr/bin/env python3
import os
import subprocess
import sys
import time

# ---------------------------------------------------
# Helper function to execute commands
# ---------------------------------------------------
def run(cmd):
    print(f"\n[RUN] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(1)

# ---------------------------------------------------
# INSTALL HAPROXY (LOAD BALANCER)
# ---------------------------------------------------
def setup_loadbalancer():
    print("\n==============================")
    print("  Installing Load Balancer")
    print("==============================")

    run("sudo apt update -y")
    run("sudo apt install -y haproxy")

    # Copy configuration
    run("sudo cp haproxy.cfg /etc/haproxy/haproxy.cfg")

    # Restart service
    run("sudo systemctl restart haproxy")
    run("sudo systemctl enable haproxy")

    print("\n[OK] Load Balancer installed successfully!\n")

# ---------------------------------------------------
# INSTALL APP1 (FLASK + POSTGRESQL)
# ---------------------------------------------------
def setup_app1():
    print("\n==============================")
    print("     Installing APP1 (DB)")
    print("==============================")

    run("sudo apt update -y")
    run("sudo apt install -y python3 python3-pip postgresql postgresql-contrib")

   

    print("\n[INFO] Installing Python requirements...")
    run("pip3 install -r requirements.txt --break-system-packages")

    print("\n[INFO] Configuring systemd service...")

    # Copy service file
    run("sudo cp flask.service /etc/systemd/system/flask.service")

    # Modify service to use app_db.py instead of app.py
    run("sudo sed -i 's/app.py/app_db.py/' /etc/systemd/system/flask.service")

    # Reload and enable
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable flask")
    run("sudo systemctl restart flask")
    
    print("\n[INFO] Creating PostgreSQL database...")


     # Create DB, user and permissions
    db_commands = """
    CREATE DATABASE labdb;
    CREATE USER lab WITH ENCRYPTED PASSWORD 'lab123';
    GRANT ALL PRIVILEGES ON DATABASE labdb TO lab;
    """
    
    run(f"sudo -u postgres psql -c \"{db_commands}\"")
    
    print("\n[OK] APP1 installed successfully!\n")

# ---------------------------------------------------
# INSTALL APP2 (FLASK ONLY)
# ---------------------------------------------------
def setup_app2():
    print("\n==============================")
    print("     Installing APP2 (No DB)")
    print("==============================")

    run("sudo apt update -y")
    run("sudo apt install -y python3 python3-pip")

    print("\n[INFO] Installing Python requirements...")
    run("pip3 install -r requirements.txt --break-system-packages")

    print("\n[INFO] Configuring systemd service...")
    run("sudo cp flask.service /etc/systemd/system/flask.service")

    # No change needed → this VM uses app.py
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable flask")
    run("sudo systemctl restart flask")

    print("\n[OK] APP2 installed successfully!\n")

# ---------------------------------------------------
# MAIN MENU
# ---------------------------------------------------
def main():
    print("""
=========================================
        LAB VM SETUP TOOL - PYTHON
=========================================

Choose the role of this VM:

[1] Load Balancer (HAProxy)
[2] APP1 (Flask + PostgreSQL)
[3] APP2 (Flask only)
[0] Exit
""")

    choice = input("Select option: ")

    if choice == "1":
        setup_loadbalancer()
    elif choice == "2":
        setup_app1()
    elif choice == "3":
        setup_app2()
    else:
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()

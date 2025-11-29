import sys
import yaml

def generate_netplan(ip, mask, gateway, filename):
    # Monta o YAML no formato exigido pelo Netplan
    data = {
        "network": {
            "version": 2,
            "ethernets": {
                "enp0s3": {
                    "addresses": [f"{ip}/{mask}"],
                    "gateway4": gateway,
                    "nameservers": {
                        "addresses": ["8.8.8.8", "8.8.4.4"]
                    }
                }
            }
        }
    }

    # Salva no arquivo
    with open(filename, "w") as f:
        yaml.dump(data, f, sort_keys=False)

    print(f"[OK] Arquivo {filename} gerado com sucesso!")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso:")
        print("  python3 generate_netplan.py <ip> <mask> <gateway> <arquivo.yaml>")
        print("\nExemplo:")
        print("  python3 generate_netplan.py 192.168.2.211 24 192.168.2.1 /etc/netplan/50-cloud-init.yaml")
        sys.exit(1)

    ip = sys.argv[1]
    mask = sys.argv[2]
    gateway = sys.argv[3]
    filename = sys.argv[4]

    generate_netplan(ip, mask, gateway, filename)

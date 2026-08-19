#!/bin/bash
# network_setup.sh - Configura rede para o BoxTwin (ex: IP fixo, WPA2-Enterprise)

set -e

echo "=== Configuração de rede do BoxTwin ==="

# 1. IP Fixo via dhcpcd (exemplo)
read -p "Deseja configurar IP fixo? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -p "Endereço IP desejado (ex: 192.168.1.100/24): " IPADDR
    read -p "Gateway (ex: 192.168.1.1): " GATEWAY
    read -p "DNS (ex: 8.8.8.8): " DNS
    sudo bash -c "cat >> /etc/dhcpcd.conf <<EOF
interface eth0
static ip_address=$IPADDR
static routers=$GATEWAY
static domain_name_servers=$DNS
EOF"
    echo "IP fixo configurado. Reinicie o serviço: sudo systemctl restart dhcpcd"
fi

# 2. Wi-Fi corporativo (WPA2-Enterprise)
read -p "Deseja configurar Wi-Fi corporativo? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -p "SSID da rede: " SSID
    read -p "Usuário (EAP): " USER
    read -s -p "Senha: " PASS
    echo
    sudo bash -c "cat > /etc/wpa_supplicant/wpa_supplicant.conf <<EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BR

network={
    ssid=\"$SSID\"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity=\"$USER\"
    password=\"$PASS\"
    phase2=\"auth=MSCHAPV2\"
}
EOF"
    echo "Configuração Wi-Fi adicionada. Reinicie a interface: sudo wpa_cli -i wlan0 reconfigure"
fi

echo "Configuração de rede concluída. Reinicie o Raspberry para aplicar todas as mudanças."
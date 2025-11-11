#!/bin/bash
# Actualiza e instala dependencias
sudo apt update -y
sudo apt install -y python3-pip python3-venv git

# Crea el entorno virtual
cd /home/ubuntu
python3 -m venv venv
source venv/bin/activate

# Clona tu repo de GitHub
git clone https://github.com/Vrtx566/tallerEC2.git
cd tallerEC2

# Instala las dependencias
pip install -r requirements.txt

# Copia el archivo del servicio
sudo cp fastapi.srv /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi.srv
sudo systemctl start fastapi.srv

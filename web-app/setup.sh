#! /bin/bash
apt install git
apt install python3.11
apt install python3.11-venv
apt install screen

python3.11 -m venv venv
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Finished setup!"
echo "Add the email pw as file ..."
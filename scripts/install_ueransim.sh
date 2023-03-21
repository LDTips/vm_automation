#!/bin/bash
# Tested once. Works. Requires some more extensive testing
# This script is less complex than open5gs
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed" 1>&2
  exit 1
fi

SRC_USERNAME=$(id -nu $SUDO_UID)
SRC_PATH=$(eval echo "~$SRC_USERNAME")
# $HOME should be root home dir
if [[ -d "$HOME/UERANSIM" ]] || [[ -d "$SRC_PATH/UERANSIM" ]]; then
  echo "UERANSIM is most likely installed. UERANSIM folder exists at home dir. Installation cancelled" 1>&2
  exit 2
fi

# Fetch dependencies
apt-get install dialog apt-utils -y  # Required to not encounter "tty required" error
apt-get update
apt-get install build-essential libsctp-dev lksctp-tools iproute2 g++ gcc -y
snap install cmake --classic

# Fetch UERANSIM files
cd "$SRC_PATH" || exit
git clone https://github.com/aligungr/UERANSIM
chown "$SRC_USERNAME:$SRC_USERNAME" ./UERANSIM/  # Git clone was made as root, so we need to change ownership
# Build UERANSIM. Note: takes some time. Recommended to make some coffee or tea in the meantime
cd "$SRC_PATH/UERANSIM" || exit
make

# Change hostname and hosts file
echo "UERANSIM" > /etc/hostname
sed -i '2i 127.0.1.1 UERANSIM' /etc/hosts # 2i - insert at 2nd line

echo "Rebooting in 5 seconds..."
sleep 5
shutdown -r now

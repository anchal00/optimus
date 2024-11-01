#!/usr/bin/env bash

# Check if optimus is installed
which optimus

if [ $? -ne 0 ]; then
  echo "Error ! Failed to locate optimus. Please make sure you have installed optimus"
  exit 1
fi

# Stop systemd resolver daemon
eval $(sudo systemctl stop systemd-resolved.service)

# Configure your local dns resolver to point to optimus
eval $(sed s/127.0.0.53/127.0.0.1/g /run/systemd/resolve/stub-resolv.conf > stub-resolv.conf)
eval $(sudo mv stub-resolv.conf /run/systemd/resolve/stub-resolv.conf)

sudo $(which optimus) "$@"


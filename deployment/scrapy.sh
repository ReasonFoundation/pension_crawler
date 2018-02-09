#!/bin/bash


# Better print function

function _print() {
  echo
  echo "#######################################################################"
  echo "# $1"
  echo "#######################################################################"
  echo
}


# Check user permissions

function check_root() {
  if [[ $EUID > 0 ]]; then
    _print "Please run script as root/sudo user."
    exit 1
  fi
  _print "Running script as root/sudo user."
}

check_root


# Set environment variables

function configure_environment() {
  ENVIRONMENT=$(sed 's/^/export /' secrets)
  echo -e "\n$ENVIRONMENT" >> ~/.bashrc
  source ~/.bashrc
  _print "Environment variables set."
}


# Install system dependencies

function configure_system() {
  PACKAGES=(
    python3
    python3-dev
    python3-pip
    libxml2-dev
    libxslt1-dev
    zlib1g-dev
    libffi-dev
    libssl-dev
  )
  apt-get update && apt-get install -y ${PACKAGES[@]}
  _print "Installed system dependencies."
}


# Install python dependencies

function configure_python() {
  pip3 install -r requirements.txt
  _print "Installed python dependencies."
}


# Run functions from script

function main() {
  configure_environment
  configure_system
  configure_python
  _print "Script finished."
}

main

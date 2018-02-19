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


# Sleep for n seconds

function do_wait() {
  _print "Sleeping for $1 seconds"
  sleep $1
}


# Install system dependencies

function configure_system() {
  PACKAGES=(
    supervisor
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


# Start supervisord with environment variables

function configure_supervisor() {
  cp scrapyd.conf /etc/supervisor/conf.d/scrapyd.conf
  supervisorctl reread && supervisorctl update
  _print "Supervisord configured and running."
}


# Deploy project

function configure_scrapyd() {
  scrapyd-deploy
  _print "Scrapy project deployed."
}


# Run functions from script

function main() {
  configure_system
  configure_python
  configure_supervisor
  do_wait 10
  configure_scrapyd
  _print "Script finished."
}

main

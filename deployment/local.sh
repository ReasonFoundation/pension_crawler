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


# Create output directories

function configure_directories() {
  mkdir ../data/output
  DIRECTORIES=(bing google sites)
  for dir in ${DIRECTORIES[@]}
  do
    mkdir ../data/output/$dir
  done
  _print "Created output directories."
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
  configure_directories
  configure_system
  configure_python
  _print "Script finished."
}

main

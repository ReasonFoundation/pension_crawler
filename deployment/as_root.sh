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
    libpulse-dev
    antiword
    unrtf
    poppler-utils
    pstotext
    tesseract-ocr
    flac
    ffmpeg
    lame
    libmad0
    libsox-fmt-mp3
    sox
    libjpeg-dev
    swig
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


# Add weekly cronjob

function configure_cron() {
  SCRAPY="/usr/local/bin/scrapy"
  JOB="1 0 * * 0 cd /home/reason/pension_crawler/ && $SCRAPY crawl sites"
  (crontab -u reason -l ; echo "$JOB") | crontab -u reason -
  sudo systemctl restart cron.service
  _print "Cronjob started."
}


# Run functions from script

function main() {
  configure_system
  configure_python
  configure_cron
  _print "Script finished."
}

main

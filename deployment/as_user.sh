#!/bin/bash


# Better print function

function _print() {
  echo
  echo "#######################################################################"
  echo "# $1"
  echo "#######################################################################"
  echo
}


# Create output directories

function configure_directories() {
  mkdir ../data/temp
  mkdir ../data/output
  DIRECTORIES=(bing google sites)
  for dir in ${DIRECTORIES[@]}
  do
    mkdir ../data/output/$dir
  done
  _print "Created output directories."
}


# Run functions from script

function main() {
  configure_directories
  _print "Script finished."
}

main

#!/bin/bash

# This script will run kdb+ locally and listen on $KDB_PORT

source .env

$KDB_Q_PATH db -p $KDB_PORT

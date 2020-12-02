#!/usr/bin/env bash

FILE=$1
[[ -z $1 ]] && export FILE=compose/vars.env

echo 'loading env vars from: ' $FILE

export $(grep -v '^#' $FILE | xargs)

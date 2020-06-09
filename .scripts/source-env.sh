#!/usr/bin/env bash

export $(grep -v '^#' compose/vars.env | xargs)

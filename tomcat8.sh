#!/bin/bash

# sentenv.sh

if [ -z "${TOMCAT_CFG_LOADED}" ]; then
  if [ -z "${TOMCAT_CFG}" ]; then
    TOMCAT_CFG="/etc/tomcat8/tomcat8.conf"
  fi
  . $TOMCAT_CFG
fi

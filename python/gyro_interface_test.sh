#!/bin/bash

if i2cdetect -y -r 1 | grep 6; then
  echo "NO GYRO FOUND"
else
  echo "GYRO FOUND"
  python gyro_polling_test.py
fi

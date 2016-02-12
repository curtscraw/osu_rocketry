#!/bin/bash

if `i2cdetect -y -r 1 | grep 6b`; then
  echo "NO GYRO FOUND"
else
  echo "GYRO FOUND"
  python gyro_polling_test.py
fi

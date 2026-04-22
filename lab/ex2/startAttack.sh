#!/bin/bash

BASE="$(cd "$(dirname "$0")" && pwd)"

cp hostapd.conf $BASE/krackattacks-script/hostapd/
cp modified-krack-test-client.py $BASE/krackattacks-script/krackattack/
source $BASE/krackattacks-script/krackattack/venv/bin/activate;
cd "$BASE/krackattacks-script/krackattack"
python3 modified-krack-test-client.py --debug
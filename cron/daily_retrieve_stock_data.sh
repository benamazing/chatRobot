#!/usr/bin/sh

cd /data/study/python/chatRobot/cron
python daily_retrieve_stock_data.py
python daily_retrieve_dd.py
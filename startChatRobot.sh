#!/usr/bin/sh

cd /data/study/python/chatRobot
total_line=`ps -ef|grep -i chatRobot|grep start.py|wc -l`
if [ $total_line -eq 0 ]
then
        ./deploy.sh
	nohup /usr/bin/python /data/study/python/chatRobot/start.py 2>&1 &
	ps -ef|grep chatRobot|grep start.py
	echo "---> Started!"
else
	echo "---> Already find another chatRobot process running:"
	ps -ef |grep chatRobot|grep -v grep
	echo "---> Quit!"
fi


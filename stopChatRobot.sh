#!/usr/bin/sh

total_line=`ps -ef|grep -i chatRobot|grep start.py|wc -l`
if [ $total_line -eq 0 ]
	then
		echo "No chatRobot is running, quiting..."
	else
		echo "--> Find below chatRobot running: "
		ps -ef|grep chatRobot|grep start.py
		echo "--> Killing the process..."
		ps -ef|grep chatRobot|grep start.py|awk '{print $2}'|xargs kill -9
		echo "--> Done!"
fi

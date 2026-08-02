#!/bin/bash
cd /home/opencode/team4/pramuka-jabar-superapp/frontend
setsid nohup python3 spa_server.py 3004 dist >> frontend.log 2>&1 < /dev/null &
echo $! > frontend.pid
sleep 2
echo "Frontend PID: $(cat frontend.pid)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:3004

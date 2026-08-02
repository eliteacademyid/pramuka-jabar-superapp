#!/bin/bash
export PATH="/home/opencode/.local/bin:$PATH"
cd /home/opencode/team4/pramuka-jabar-superapp/backend
setsid nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 >> backend.log 2>&1 < /dev/null &
echo $! > backend.pid
sleep 4
echo "PID: $(cat backend.pid)"
tail -5 backend.log

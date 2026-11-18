#!/bin/sh
# Usage: scripts/remote.sh HOST LOGFILE command...   (runs detached on HOST with scripts/env.sh)
host=$1; log=$2; shift 2
ssh -o BatchMode=yes "$host" ". /data/rbg/users/linrui/llada/scripts/env.sh && nohup $* > $log 2>&1 < /dev/null & echo launched on $host pid \$!"

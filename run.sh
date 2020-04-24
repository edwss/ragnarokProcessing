exec ./virtualmachine.sh 5900 01 machine-1  4444 &
exec ./virtualmachine.sh 5901 02 merchant  4445 &

source env/bin/activate
exec python socket_server.py 4300 5900 4444 &
exec python socket_server.py 4301 5901 4445 &
#!/bin/bash
while true; do
    python3 main.py
    if [ $? -ne 0 ]; then
        echo "Script crashed with exit code $?. Restarting..." >&2
    else
        echo "Script exited normally."
        exit 0
    fi
    sleep 1  # Prevents a rapid restart loop
done

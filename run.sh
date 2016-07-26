#!/usr/bin/env bash
(
        flock -x -w 10 200 || exit 1
        ./run.py
) 200>/var/lock/.chantel.exclusivelock

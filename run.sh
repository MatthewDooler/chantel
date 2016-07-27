#!/usr/bin/env bash
(
        flock -x -w 59 200 || exit 1
        ./run.py
) 200>/var/lock/.chantel.exclusivelock

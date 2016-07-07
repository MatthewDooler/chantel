#!/usr/bin/env bash
lt --port 8080 --subdomain chantel | at now + 1 minutes
lt --port 8081 --subdomain chantelws | at now + 1 minutes
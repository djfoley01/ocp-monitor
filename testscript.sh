#!/bin/bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/register -d "fullname=ocp" -d "email=ocp@test.com" -d "password=temp123" -d "password_conf=temp123" -d "ocp_admin=true"
token=$(curl -X POST http://127.0.0.1:5000/api/v1/auth/login -d "email=ocp@test.com" -d "password=temp123" | jq .token | sed 's/"//g')
curl -X GET -H "Authorization: $token" -H "Content-Type: application/json" http://127.0.0.1:5000/api/v1/ocp/nodes

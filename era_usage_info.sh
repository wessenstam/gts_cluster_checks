#!/usr/bin/env bash

CURL_HTTP_OPTS="--max-time 25 --silent -k --header Content-Type:application/json --header Accept:application/json  --insecure"

PRISM_ADMIN="admin"
PE_PASSWORD='nutanix/4u'

cluster_list="./eraservers.txt"
clusters=`cat $cluster_list`

#export name=$(tail -n +2 text.txt | sed '$d' | jq '.name' | tr -d \")

for cluster in $(cat $cluster_list)
do
  echo "**********************************************************************"
  echo ""
  echo "Listing out Clones for cluster $cluster"
  clone_list=$(curl ${CURL_HTTP_OPTS} --request GET https://$cluster:8443/era/v0.8/clones --user ${PRISM_ADMIN}:${PE_PASSWORD} | tr -dc "[:print:]\n" | jq '.[].name'| tr -d \")
  echo "Clones on $cluster are:"
  echo "$clone_list"
  echo ""
  echo "Listing out Time Machines for cluster $cluster"
  tms_list=$(curl ${CURL_HTTP_OPTS} --request GET https://$cluster:8443/era/v0.8/tms --user ${PRISM_ADMIN}:${PE_PASSWORD} | tr -dc "[:print:]\n" | jq '.[].name'| tr -d \")
  echo "Time Machines on $cluster are:"
  echo "$tms_list"
  echo ""
  echo "**********************************************************************"
done

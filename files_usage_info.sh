#!/usr/bin/env bash

CURL_HTTP_OPTS="--max-time 25 --silent -k --header Content-Type:application/json --header Accept:application/json  --insecure"

PRISM_ADMIN="admin"
PE_PASSWORD='techX2020!'

cluster_list="./pe_clusters.txt"
clusters=`cat $cluster_list`

for cluster in $(cat $cluster_list)
do
  echo "**********************************************************************"
  echo ""
  echo "Listing out Shares for cluster $cluster"
  share_list=$(curl ${CURL_HTTP_OPTS} --request GET https://$cluster:9440/PrismGateway/services/rest/v1/vfilers/shares --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .name' | tr -d \")
  echo "Shares on $cluster are:"
  echo "$share_list"
  echo ""
  echo "**********************************************************************"
done

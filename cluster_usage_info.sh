#!/usr/bin/env bash

CURL_HTTP_OPTS="--max-time 25 --silent -k --header Content-Type:application/json --header Accept:application/json  --insecure"

PRISM_ADMIN="admin"
PE_PASSWORD='techX2020!'

cluster_list="./pc_clusters.txt"
clusters=`cat $cluster_list`

for cluster in $(cat $cluster_list)
do
  echo "**********************************************************************"
  echo ""
  echo "Listing out networks for cluster $cluster"
  network_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/subnets/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .spec.name' | tr -d \")
  echo "Networks on $cluster are:"
  echo "$network_list"
  echo ""
  echo "Listing out Categories for cluster $cluster"
  categories_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/categories/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .name' | tr -d \")
  echo "Categories on $cluster are:"
  echo "$categories_list"
  echo ""
  echo "Listing out Network Security Rules for cluster $cluster"
  network_security_rules_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/network_security_rules/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .spec.name' | tr -d \")
  echo "Network Security Rules on $cluster are:"
  echo "$network_security_rules_list"
  echo ""
  echo "Listing out Calm BPs for cluster $cluster"
  bp_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/blueprints/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .status.name' | tr -d \")
  echo "Calm BPs on $cluster are:"
  echo "$bp_list"
  echo ""
  echo "Listing out Calm Apps for cluster $cluster"
  app_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/apps/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .status.name' | tr -d \")
  echo "Calm Apps on $cluster are:"
  echo "$app_list"
  echo ""
  echo "Listing out VMs for cluster $cluster"
  vm_list=$(curl ${CURL_HTTP_OPTS} --request POST https://$cluster:9440/api/nutanix/v3/vms/list --user ${PRISM_ADMIN}:${PE_PASSWORD} --data '{}' | jq -r '.entities[] | .spec.name' | tr -d \")
  echo "VMs on $cluster are:"
  echo "$vm_list"
  echo ""
  echo "**********************************************************************"
done

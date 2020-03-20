# This script is to check the deployed clusters for the Tech Summits to see if the blueprints are running.
# 07-03-2020: Willem Essenstam - Initial version 0.1
# Check to see if there is a named App and what it's status is. If not running start countermeasures...

import requests
import json
import urllib3
import time

#####################################################################################################################################################################
# This function is to get the to see if the initialisation of the cluster has been run (EULA, PULSE, Network)
#####################################################################################################################################################################
def get_json_data(ip_address,get_url,json_data,method,user,passwd,value):
    #Get the URL and compose the command to get the request from the REST API of the cluster
    url="https://"+ip_address+":9440/"+get_url
    header_post = {'Content-type': 'application/json'}

    # if method is not set assume GET
    if method=="":
        method="get"

    # Set the right requests based on GET, POST, delete
    if method=="get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps Error: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    elif method=="post":
        try:
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    elif method=="delete":
        try:
            page=requests.delete(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)


#####################################################################################################################################################################
# BP + App checks
#####################################################################################################################################################################

def checks_to_run(server_ip,user,passwd):

    server_ip_pc = server_ip[:len(server_ip) - 2] + "39"

    print("------------------------------------------------")
    print("- PC at " + server_ip_pc)

    # What is the status of the OSS
    # Is there and objectstore?
    url = "oss/api/nutanix/v3/groups"
    payload = '{"entity_type":"objectstore","group_member_sort_attribute":"name","group_member_sort_order":"ASCENDING","group_member_count":20,"group_member_offset":0,"group_member_attributes":[{"attribute":"name"},{"attribute":"domain"},{"attribute":"num_msp_workers"},{"attribute":"usage_bytes"},{"attribute":"num_buckets"},{"attribute":"num_objects"},{"attribute":"num_alerts_internal"},{"attribute":"client_access_network_ip_used_list"},{"attribute":"total_capacity_gib"},{"attribute":"last_completed_step"},{"attribute":"state"},{"attribute":"percentage_complete"},{"attribute":"ipv4_address"},{"attribute":"num_alerts_critical"},{"attribute":"num_alerts_info"},{"attribute":"num_alerts_warning"},{"attribute":"error_message_list"},{"attribute":"cluster_name"},{"attribute":"client_access_network_name"},{"attribute":"client_access_network_ip_list"},{"attribute":"buckets_infra_network_name"},{"attribute":"buckets_infra_network_vip"},{"attribute":"buckets_infra_network_dns"},{"attribute":"total_memory_size_mib"},{"attribute":"total_vcpu_count"},{"attribute":"num_vcpu_per_msp_worker"}]}'
    value = ''
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    for key in json_search['group_results'][0]['entity_results'][0]['data']:
        if key['name']=="state":
            if key['values'][0]['values'][0]!="COMPLETE":
                if key['values'][0]['values'][0]=="PENDING":
                    print("Application is being deployed. Skipping")
                    continue
                else:
                    print("Error found in the application. Need counter measures...")
            else:
                print("All good!!")



#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Use a file with parameters to run the checks
file=open("cluster1.txt","r")
file_line=file.readlines()
for line in file_line:
    if "#" not in line:
        line_dict=line.split("|")
        server_ip_var=line_dict[0]
        user_name='admin'
        passwd_var=line_dict[1]
        checks_to_run(server_ip_var,user_name,passwd_var)


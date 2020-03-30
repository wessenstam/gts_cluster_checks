# This script is to check the deployed clusters for the Tech Summits to see if everything has been deployed as it should be.
# 16-02-2020: Willem Essenstam - Initial version 0.1
# Order:
# 1. Check the PE deployment:   a) Eula
#                                b) Pulse
#                                c) Network
#                                d) is AD configured
#                                e) DNS servers
#                                f) NTP servers
# 2. Check PC deployment:       a) DNS servers
#                                b) is AD integrated
#                                c) is Calm enabled
#                                d) is Karbon enabled
#                                e) is Objects enabled
#                                f) has LCM run
#                                g) has flow been enabled
#                                h) do we have the blueprints?
#                                    1. CICD
#                                    2. Citrix
#                                    3. Era deployment
#                                i) Do we have the images uploaded?

import requests
import json
import urllib3
import sys


#####################################################################################################################################################################
# This function is to get all the values that we are looking for in the json returns
#####################################################################################################################################################################
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

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

    # Set the right requests based on GET or POST
    if method=="get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=15)
            page.raise_for_status()
            if value != "":
                json_data = extract_values(json.loads(page.text), value)
            else:
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

    else:
        try:
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
            page.raise_for_status()
            if value != "":
                json_data = extract_values(json.loads(page.text), value)
            else:
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

    # What is the status code of the request?


#####################################################################################################################################################################
# PC Checks
#####################################################################################################################################################################

def checks_to_run(server_ip,user,passwd):

    server_ip_pc = server_ip[:len(server_ip) - 2] + "39"

    print("------------------------------------------------")
    print("- PC at " + server_ip_pc)

    # Do we have the DNS servers Configured?
    url = "PrismGateway/services/rest/v2.0/cluster/name_servers"
    payload = ''
    value = ""
    method = ""
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

    # If we have seen an error, just return so we can move to the next one and just mention the issue
    if "Error" in str(json_search):
        return

    # Create the right DNS server to search for
    octet_dict = server_ip.split(".")
    dns_server = octet_dict[0]+'.'+octet_dict[1]+'.'+octet_dict[2]+".41"

    if not dns_server in json_search:
        print("PC at " + server_ip + " has not got the Pirmary DNS configured...")

    # Do we have the AD Configured?
    url = "PrismGateway/services/rest/v1/authconfig/directories/"
    payload = ''
    value = "name"
    method = ""
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if not "NTNXLAB" in json_search:
        print("Cluster has not got the Domain Controller connected...")

    # Do we have Calm enabled?
    url = "api/nutanix/v3/services/nucalm/status"
    payload = ''
    value = "service_enablement_status"
    method = ""
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if not "ENABLED" in json_search:
        print("Calm has not been enabled...")

    # Do we have Karbon enabled?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"k8_cluster_entity","query_name":"eb:data:General-1555061817690","grouping_attribute":" ","group_count":3,"group_offset":0,"group_attributes":[],"group_member_count":40,"group_member_offset":0,"group_member_sort_order":"DESCENDING","group_member_attributes":[]}'
    value = "entity_type"
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if not "k8_cluster_entity" in json_search:
        print("Karbon has not been enabled...")

    # Do we have Objects enabled?
    url = "oss/api/nutanix/v3/groups"
    payload = '{"entity_type":"objectstore"}'
    value = "entity_type"
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if not "objectstore" in json_search:
        print("Objects has not been enabled...")

    # Did LCM run?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type": "lcm_entity_v2","group_member_count": 500,"group_member_attributes": [{"attribute": "id"}, {"attribute": "uuid"}, {"attribute": "entity_model"}, {"attribute": "version"}, {"attribute": "location_id"}, {"attribute": "entity_class"}, {"attribute": "description"}, {"attribute": "last_updated_time_usecs"}, {"attribute": "request_version"}, {"attribute": "_master_cluster_uuid_"}, {"attribute": "entity_type"}, {"attribute": "single_group_uuid"}],"query_name": "lcm:EntityGroupModel","grouping_attribute": "location_id","filter_criteria": "entity_model!=AOS;entity_model!=NCC;entity_model!=PC;_master_cluster_uuid_==[no_val]"}'
    value = ""
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    # Check MSP version
    if "1.0.5" not in str(json_search):
        print("Micro services have not been updated...")
    # Check Objects version
    if "2.0" not in str(json_search):
        print("Objects has not been updated...")
    # Check Calm version
    if "2.9.8" not in str(json_search):
        print("Calm and Epsilon have not been updated...")
    # Check Karbon version
    if "2.0" not in str(json_search):
        print("Karbon has not been updated...")

    # Do we have Security Rules (Flow enabled) enabled?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"network_security_rule"}'
    value = "filtered_entity_count"
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if "2" not in str(json_search):
        print("Flow has not been enabled...")
        print("Start countermeasures on Flow...")
        url="https://"+server_ip_pc+":9440/api/nutanix/v3/services/microseg"
        pay_load='{"state":"ENABLE"}'
        header_post = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        json_reply=start_counter_measures(url, pay_load, user, passwd, header_post)
        if not json_reply:
            print("Countermeasures failed. Please run via the UI...")
        else:
            print("Countermeasures started. Flow should be enabled..")


    # Do we have Blueprints uploaded?
    url = "api/nutanix/v3/blueprints/list"
    payload = '{}'
    value = "total_matches"
    method = "post"
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    if "4" not in str(json_search):
        print("The amount of Blueprints on the PC is "+str(json_search)+" and not the initial number of 4...")

    # Are the Apps running? Era, Citrix and Karbon
    app_check_list=('Era Server','Citrix Infra','KarbonClusterDeployment')
    for app_name in app_check_list:
        url = "api/nutanix/v3/apps/list"
        payload = '{"filter":"name==' + app_name + '"}'
        method = "post"
        value = ''
        json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

        # ***************************************************************************
        try:
            # We found the to be searched app. Check if the App is running
            if json_search['entities'][0]['status']['state'] == "running":
                continue
            elif json_search['entities'][0]['status']['state'] == "provisioning":
                print("App "+app_name+" is being provisioned. Please check later again....")
            else:
                print("App "+app_name+" is in the Error state. Please run the check_bp.py script to restart the app....")
        except IndexError:
            print("The app "+app_name+" has not been found on the PC......")

    # Check if we have the images in there
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"image","query_name":"eb:data-1582633054821","grouping_attribute":" ","group_count":3,"group_offset":0,"group_attributes":[],"group_member_count":40,"group_member_offset":0,"group_member_sort_attribute":"name","group_member_sort_order":"ASCENDING","group_member_attributes":[{"attribute":"name"}]}'
    value = ""
    method = "post"
    json_search_images = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    print("Amount of images at the PC is " + str(json_search_images['total_entity_count']))

    if int(json_search_images['total_entity_count']) < 28:

        #Check if there are tasks running. If so skip this PC wrt images upload
        url = "PrismGateway/services/rest/v2.0/tasks/list"
        payload = '{"include_completed": false,"include_subtasks_info": false}'
        value = "total_entities"
        method = "post"
        json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
        if "0" not in str(json_search):
            print("Tasks are running on the cluster ("+str(json_search)+")... Skipping this cluster...")
        else:
            # Get the right DFS to pull the images from
            if str(octet_dict[1]) == "42" or str(octet_dict[1]) == "38":
                source_ip = "10.42.38.10/images"
            else:
                source_ip = "10.55.75.10"

            print("As no tasks are running; Checking which image is not at the PC...")
            images = ("ERA-Server-build-1.2.1.qcow2", "CentOS7.qcow2", "Windows2016.qcow2", "Linux_ToolsVM.qcow2",
                      "move-3.4.1.qcow2", "Win10v1903.qcow2", "WinToolsVM.qcow2", "GTSOracle/19c-april/19c-bootdisk.qcow2",
                      "MSSQL-2016-VM.qcow2", "GTSOracle/19c-april/19c-disk3.qcow2", "GTSOracle/19c-april/19c-disk5.qcow2",
                      "GTSOracle/19c-april/19c-disk4.qcow2", "GTSOracle/19c-april/19c-disk6.qcow2",
                      "GTSOracle/19c-april/19c-disk7.qcow2", "GTSOracle/19c-april/19c-disk1.qcow2","GTSOracle/19c-april/19c-disk2.qcow2",
                      "GTSOracle/19c-april/19c-disk9.qcow2", "GTSOracle/19c-april/19c-disk8.qcow2",
                      "HYCU/Mine/HYCU-4.0.3-Demo.qcow2", "veeam/VeeamAHVProxy2.0.404.qcow2",
                      "Citrix_Virtual_Apps_and_Desktops_7_1912.iso","Nutanix-VirtIO-1.1.5.iso","FrameCCA-2.1.6.iso","FrameCCA-2.1.0.iso",
                      "FrameGuestAgentInstaller_1.0.2.2_7930.iso","veeam/VBR_10.0.0.4442.iso")
            for image_check in sorted(images):
                if image_check not in str(json_search_images):
                    print("Image " + image_check + " is not available in the PC on " + server_ip_pc + "...")
                    print("Starting the countermeasure to get the image "+image_check+" in....")
                    if "qcow2" in str(image_check):
                        image_type="DISK_IMAGE"
                    else:
                        image_type="ISO_IMAGE"

                    _http_body ='{"action_on_failure":"CONTINUE","execution_order":"SEQUENTIAL","api_request_list":[{"operation":"POST","path_and_params":"/api/nutanix/v3/images","body":{"spec":{"name":"'+image_check+'", "description":"'+image_check+'", "resources":{"image_type":"'+image_type+'","source_uri":"http://'+source_ip+"/"+image_check+'"}},"metadata":{"kind":"image"}, "api_version":"3.1.0"}}], "api_version":"3.0"}'
                    header_post = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    url="https://"+server_ip_pc+':9440/api/nutanix/v3/batch'
                    start_counter_measures(url,_http_body,user,passwd,header_post)

#####################################################################################################################################################################
# Start the countermeasures for the API calls to correct issues found
#####################################################################################################################################################################

def start_counter_measures(url, pay_load, user, passwd,header_post):
    try:
        page = requests.post(url, verify=False, auth=(user, passwd), data=pay_load, headers=header_post)
        page.raise_for_status()
        return page.json()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)


#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Use a file with parameters to run the checks
file=open("cluster.txt","r")
file_line=file.readlines()
for line in file_line:
    if "#" not in line:
        line_dict=line.split("|")
        server_ip_var=line_dict[0]
        user_name='admin'
        passwd_var=line_dict[1]
        checks_to_run(server_ip_var,user_name,passwd_var)

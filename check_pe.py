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
    header_post = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # if method is not set assume GET
    if method=="":
        method="get"

    # Set the right requests based on GET or POST
    if method=="get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=10)
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
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post)
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
# PE Checks
#####################################################################################################################################################################

def checks_to_run(server_ip,user,passwd):

    print("------------------------------------------------")
    print("- PE at " + server_ip)


    # Get the amount of nodes in the cluster. Needs to be 4
    url = "PrismGateway/services/rest/v2.0/hosts"
    payload=""
    value="total_entities"
    method=""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    # If we have seen an error, just return so we can move to the next one and just mention the issue
    if "Error" in str(json_search):
        return

    if not "4" in str(json_search):
        print("Our cluster is not configured with 4 nodes....")


    # Get the Initial settings test done. 1. Eula
    url = "PrismGateway/services/rest/v1/eulas"
    payload = ""
    value = "eulaAcceptedTimeInMilliSecs"
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    if json_search == "[]":
        print("EULA has not been accepted....")

    # Get the Initial settings test done. 2. Pulse disabled
    url = "PrismGateway/services/rest/v1/pulse"
    payload = ""
    value = "enable"
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    if json_search == "[false]":
        print("Pulse is still enabled....")

    # Do we have the two networks?
    url = "api/nutanix/v3/subnets/list"
    payload = '{"kind":"subnet"}'
    value = "name"
    method = "post"
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    if not "Primary" in json_search:
        print("Primary network has not been created...")
    if not "Secondary" in json_search:
        print("Secondary network has not been created...")
    else:
        # Setting the right vlan id calculation based on the third octet and in 10.32
        base_ip_dict=server_ip.split(".")
        if int(base_ip_dict[1])==38:
            if int(base_ip_dict[2]) > 169:
                vlan_id_calc = int(base_ip_dict[2])*10+3
            else:
                vlan_id_calc = int(base_ip_dict[2])*10+1
        else:
            vlan_id_calc = int(base_ip_dict[2])*10+1

        # Grab the VLAN ID from the secondary network via the json we received earlier
        url = "api/nutanix/v3/subnets/list"
        payload = '{"kind":"subnet"}'
        value = ""
        method = "post"
        json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
        json_vlan_id=json_search["entities"][1]["status"]["resources"]["vlan_id"]
        if json_vlan_id != vlan_id_calc:
            print("Wrong setting of VLAN ID on the secondary network.....")

    # Do we have the AD Configured?
    url = "PrismGateway/services/rest/v1/authconfig/directories/"
    payload = ''
    value = "name"
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    if not "NTNXLAB" in json_search:
        print("Cluster has not got the Domain Controller connected...")

    # Do we have the DNS servers Configured?
    url = "PrismGateway/services/rest/v2.0/cluster/name_servers"
    payload = ''
    value = ""
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    if str(json_search)=="[]":
        print("Cluster has not got the Primary DNS configured...")

    # Do we have the NTP servers Configured?
    url = "PrismGateway/services/rest/v2.0/cluster/ntp_servers"
    payload = ''
    value = ""
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    if int(len(json_search)) < 5:
        print("Cluster has not got the NTP servers configured...")

    # Is the FileServer deployed?
    url="PrismGateway/services/rest/v1/vfilers"
    payload=''
    value="name"
    method=""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    if not "BootcampFS" in str(json_search):
        print("Cluster has not got the FileServer deployed...")

    # Is the FileServer deployed?
    url = "PrismGateway/services/rest/v2.0/analyticsplatform"
    payload = ''
    value = "is_deployed"
    method = ""
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    if not "True" in str(json_search):
        print("Cluster has not got the FileAnalytics deployed...")


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





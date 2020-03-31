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

    # What is the status code of the request?


#####################################################################################################################################################################
# BP + App checks
#####################################################################################################################################################################

def checks_to_run(server_ip,user,passwd,app,bp,vm):

    server_ip_pc = server_ip[:len(server_ip) - 2] + "39"
    app_name=app
    bp_name=bp
    vm_name=vm

    print("------------------------------------------------")
    print("- PC at " + server_ip_pc)

    # What is the status of the BP to be checked?
    url = "api/nutanix/v3/apps/list"
    payload = '{"filter":"name=='+app_name+'"}'
    method = "post"
    value = ''
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

# ***************************************************************************
    try:
        # We found the to be searched app. Check if the App is running
        if json_search['entities'][0]['status']['state'] == "running":
            return
        elif json_search['entities'][0]['status']['state'] == "error":  # Need to change in error for Production
            print("The app "+app_name+" is not running. Countermeasures are needed...")

            # As the Application has an error, we need to start the counter measurements:
            # 1. Soft delete the application, as the application has an error
            # 2. Delete the VM
            # 3. Launch the blueprint again

            # *******************************************************************************************
            # Gathering needed parameters
            # 1. BP UUID
            # 2. VM UUID
            # 3. Nutanix Profile UUID
            # 4. Application UUID
            # 5. Application Profile UUID from the BP

            # Getting the App and BP UUID parameters needed from the earlier created json_search
            app_uuid = json_search['entities'][0]['metadata']['uuid']
            bp_uuid = json_search['entities'][0]['status']['resources']['app_blueprint_reference']['uuid']

            # Getting the UUID of the app Profile. This is needed to launch the BP
            url = "api/nutanix/v3/blueprints/" + bp_uuid + "/runtime_editables"
            payload = ''
            method = "get"
            value = ""
            json_app_pro_uuid = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
            app_prof_uuid = json_app_pro_uuid['resources'][0]['app_profile_reference']['uuid']

            # We need to skip this if we have no VM given by the main script...
            if vm_name:
                # Getting the UUID from the VM DDC which belongs to the APP
                url = "api/nutanix/v3/vms/list"
                payload = '{"filter":"vm_name==' + vm_name + '","kind": "vm"}'
                method = "post"
                value = ""
                json_search_vm_uuid = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
                vm_uuid = json_search_vm_uuid['entities'][0]['metadata']['uuid']


            # Execution part of this module
            # Soft delete the app
            url = "api/nutanix/v3/apps/" + app_uuid + "?type=soft"
            payload = ''
            method = "delete"
            value = ""
            json_app_del = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

            # Delete the VM if name given
            if vm_name:
                url = "api/nutanix/v3/vms/" + vm_uuid
                payload = ''
                method = "delete"
                value = ""
                json_vm_del = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
            # *******************************************************************************************

            # Checking the execution of the deletion
            # How far are we on the deletion of the Calm app? If still there, loop 60 secs and retry
            url = "api/nutanix/v3/apps/list"
            payload = '{"filter":"name=='+app_name+'"}'  # Real name is Citrix Image according to staging script
            method = "post"
            value = ''
            json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

            while len(json_search['entities']) > 0:
                print("The "+app_name+" app is still there. Waiting 30 seconds...")
                time.sleep(30)
                json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
            # *******************************************************************************************

            # If Karbon, make sure the Karbon API is responding before we move on....
            payload = {"length": 100}
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            # Set the address and make images call to get the cookies
            # We don't actually do anything with this call other than get cookies
            if "Karbon" in app:
                url = "https://" + server_ip_pc + ":9440/api/nutanix/v3/images/list"
                print("Detected Karbon app Routine...")
                try:
                    resp = requests.post(url, data=json.dumps(payload), headers=headers, auth=(user,passwd),
                                         verify=False, timeout=10)
                    # If the call went through successfully
                    if resp.ok:
                        # Set the cookie so we canmove forward to Karbon
                        # print("COOKIES={0}".format(resp.cookies['NTNX_IGW_SESSION']))
                        cookies = {'NTNX_IGW_SESSION': resp.cookies['NTNX_IGW_SESSION']}
                        # Open the connection to the Karbon server before moving on...
                        url = "https://" + server_ip_pc + ":7050/karbon/public/static/js/main.bb724a21.js"
                        try:
                            resp = requests.get(url, cookies=cookies, headers=headers, verify=False, timeout=10)
                        except requests.exceptions.RequestException as err:
                            print("OOps Error: Something Else", err)
                        except requests.exceptions.HTTPError as errh:
                            print("Http Error:", errh)
                        except requests.exceptions.ConnectionError as errc:
                            print("Error Connecting:", errc)
                        except requests.exceptions.Timeout as errt:
                            print("Timeout Error:", errt)
                            print("We are unable to get to the Karbon Server.....")
                except requests.exceptions.RequestException as err:
                    print("OOps Error: Something Else", err)
                except requests.exceptions.HTTPError as errh:
                    print("Http Error:", errh)
                except requests.exceptions.ConnectionError as errc:
                    print("Error Connecting:", errc)
                except requests.exceptions.Timeout as errt:
                    print("Timeout Error:", errt)
                    print("We are unable to get to the Karbon Server.....")

            # The app can be launched from the BP.
            url = "api/nutanix/v3/blueprints/" + bp_uuid + "/simple_launch"
            payload = '{"spec":{"app_name":"'+app_name+'","app_description":"","app_profile_reference":{"kind":"app_profile","name":"Nutanix","uuid":"' + app_prof_uuid + '"}}}'
            method = "post"
            value = ''
            json_bp_launch = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

            print(
                "Launched the " + bp_name + " blueprint, with the name: " + app_name + ". Please check PRISM Central Calm interface to see what the status is.....")

            return
        elif json_search['entities'][0]['status']['state'] == "provisioning":
            print("App " + app_name + " got status proviosioning... Check later...")
            return
        else:
            print("App "+app_name+" has got an unknown status. Please check the Prism UI for the state...")
            return
# ***************************************************************************
    except IndexError:

        # As we got a IndexError, we must conclude we don't have the application that we need to check.
        print("The "+app_name+" Application is not found...")
        url = "api/nutanix/v3/blueprints/list"
        payload = '{"filter":"name=='+bp_name+'"}'
        method = "post"
        value = ''
        json_search_bp = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

        try:
            # Get BP UUID from the json_search_bp
            bp_uuid=json_search_bp['entities'][0]['status']['uuid']

            # Use the BP UUID to get the full App Profile UUID that is needed for the launch of the BP.
            url = "api/nutanix/v3/blueprints/" + bp_uuid + "/runtime_editables"
            payload = ''
            method = "get"
            value = ""
            json_app_pro_uuid = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
            app_prof_uuid = json_app_pro_uuid['resources'][0]['app_profile_reference']['uuid']

            # Launch the BP using the earlier found UUIDs
            url = "api/nutanix/v3/blueprints/" + bp_uuid + "/simple_launch"
            payload = '{"spec":{"app_name":"'+app_name+'","app_description":"","app_profile_reference":{"kind":"app_profile","name":"Nutanix","uuid":"' + app_prof_uuid + '"}}}'
            method = "post"
            value = ''
            json_bp_launch = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)

            print("Launched the "+bp_name+" blueprint, with the name: "+app_name+". Please check PRISM Central Calm interface to see what the status is.....")
            return
        # ***************************************************************************
        except IndexError:
            print("No blueprint found with the name "+bp_name+"... Exiting this routine")
            return


    # If we have seen an error, just return so we can move to the next one and just mention the issue
    if "Error" in str(json_search):
        return


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
        checks_to_run(server_ip_var,user_name,passwd_var,'Citrix Infra','CitrixBootcampInfra','DDC')
        checks_to_run(server_ip_var, user_name, passwd_var, 'KarbonClusterDeployment','KarbonClusterDeployment','')

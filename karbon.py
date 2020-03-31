import requests
import json
import time
import urllib3
urllib3.disable_warnings()

def checks_to_run(server_ip,pc_user,pc_pass):
    ## Get Karbon Image UUID


    print("-------------------------------------------")
    print(server_ip)
    server_ip_pe = server_ip[:len(server_ip) - 2] + "37"
    K_cluster_name="KarbonClusterDeployment"
    # Needed Cluster UUID, Prim network UUID, image UUID, Get OS falvor, Clustername, pc_username, pc_passwd

    # Get Cluster UUID
    url = "https://" + server_ip_pe + ":9440/api/nutanix/v3/clusters/list"
    method="post"
    cookies = ""
    resp = get_data_pc(pc_user, pc_pass, url, method, cookies)
    resp_json = resp[0]
    cookies = resp[1]
    print(resp_json[''])

    # Get Prim network UUID


    # Get OS Flavor
    url="https://"+server_ip+":9440/karbon/acs/image/list"
    method="get"
    resp= get_data_pc(pc_user, pc_pass, url,method,cookies)
    resp_json=resp[0]
    count=0
    for images in resp_json:
        if images['version']=='ntnx-0.4':
            os_flavor=images['os_flavor']
            image_uuid=images['image_uuid']
            print(os_flavor,image_uuid)

        count+=1

"""
    # Set the address and make images call to get the cookies
    # We don't actually do anything with this call other than get cookies
    url = "https://"+server_ip+":9440/api/nutanix/v3/images/list"
    try:
        resp = requests.post(url, data=json.dumps(payload), headers=headers, auth=(pc_user, pc_pass), verify=False,timeout=10)
        # If the call went through successfully
        if resp.ok:
            # Set the cookie so we canmove forward to Karbon
            #print("COOKIES={0}".format(resp.cookies['NTNX_IGW_SESSION']))
            cookies = {'NTNX_IGW_SESSION': resp.cookies['NTNX_IGW_SESSION']}
            # Open the connection to the Karbon server before moving on...
            url = "https://" + server_ip + ":7050/karbon/acs/image/portal/list"
            try:
                resp = requests.get(url, cookies=cookies, headers=headers, verify=False, timeout=10)

                # Loop for 10 minutes, do a GET every 30 seconds
                for x in range(40):

                    # Make an image/list call, regardless of downloaded/downloading state
                    url = "https://"+server_ip+":7050/karbon/acs/image/list"
                    resp = requests.get(url, cookies=cookies, headers=headers, verify=False, timeout=10)
                    # If the call was successful, loop through the images (there may be more than one)
                    if resp.ok:
                        #Check to see if we have some images. If not rerun the call till we have more then 0 image
                        while len(json.loads(resp.content)) < 1:
                            resp = requests.get(url, cookies=cookies, headers=headers, verify=False, timeout=10)
                            print("We have not found any images yet, need to rerun the call to the Karbon server. Sleeping 30 seconds")
                            time.sleep(30)

                        for image in json.loads(resp.content):
                            # If this is our image, print status
                            if image['version'] == 'ntnx-0.4':

                                # If the image is available, download it
                                if image['status'] == 'Available':

                                    print(
                                    "\nKarbon image not found. Downloading now.")
                                    payload = {"uuid": image['uuid']}
                                    url = "https://"+server_ip+":7050/karbon/acs/image/download"
                                    resp = requests.post(url, cookies=cookies, json=payload, headers=headers, verify=False,timeout=10)

                                    # If the call went through successfully, set the new url, then loop
                                    if resp.ok:
                                        print(
                                        "Image download started.")
                                    else:
                                        print(
                                        "Image download call failed. Erroring out.")
                                        break

                                # If the image is downloaded, exit successfully
                                elif image['status'] == 'Downloaded':
                                    print("Image successfully downloaded.  Exiting.")
                                    return

                    else:
                        print("Image list call failed.  Erroring out.")
                        break

                    print("Sleeping for 30 seconds")
                    time.sleep(30)

                # If we made it this far, assume the download failed
                print("The Karbon image was not downloaded in 10 minutes. Erroring out.")
            except requests.exceptions.RequestException as err:
                print("OOps Error: Something Else", err)
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
                print("We are unable to get to the Karbon Server.....")
"""
    # If we made it this far, the nutanix/image/list call failed

def get_data_pc(pc_user,pc_pass, url,method,cookies):
    # Set the headers, payload, and creds
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = {"length": 100}
    if method=="post":
        try:
            resp = requests.post(url, data=json.dumps(payload), headers=headers, auth=(pc_user, pc_pass), verify=False,
                                 timeout=10,cookies=cookies)
            cookies = {'NTNX_IGW_SESSION': resp.cookies['NTNX_IGW_SESSION']}
            return json.loads(resp.content),cookies

        except requests.exceptions.RequestException as err:
            print("OOps Error: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            print("We are unable to get to the PRISM Central.....")
    else:
        try:
            resp = requests.get(url, headers=headers, auth=(pc_user, pc_pass), verify=False,
                                 timeout=10,cookies=cookies)
            return json.loads(resp.content), cookies

        except requests.exceptions.RequestException as err:
            print("OOps Error: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            print("We are unable to get to the PRISM Central.....")



file=open("cluster.txt","r")
file_line=file.readlines()
for line in file_line:
    if "#" not in line:
        line_dict=line.split("|")
        server_ip_var=line_dict[0]
        server_ip_pc = server_ip_var[:len(server_ip_var) - 2] + "39"
        user_name='admin'
        passwd_var=line_dict[1]
        checks_to_run(server_ip_pc,user_name,passwd_var)
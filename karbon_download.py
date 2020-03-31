import requests
import json
import time
import urllib3
urllib3.disable_warnings()

def checks_to_run(server_ip,pc_user,pc_pass):
    ## Get Karbon Image UUID
    # Set the headers, payload, and creds
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = {"entity_type": "lcm_entity_v2","group_member_count": 500,"group_member_attributes": [{"attribute": "id"}, {"attribute": "uuid"},
                {"attribute": "entity_model"}, {"attribute": "version"}, {"attribute": "location_id"}, {"attribute": "entity_class"},
                {"attribute": "description"}, {"attribute": "last_updated_time_usecs"}, {"attribute": "request_version"},
                {"attribute": "_master_cluster_uuid_"}, {"attribute": "entity_type"}, {"attribute": "single_group_uuid"}],
                "query_name": "lcm:EntityGroupModel","grouping_attribute": "location_id",
               "filter_criteria": "entity_model!=AOS;entity_model!=NCC;entity_model!=PC;_master_cluster_uuid_==[no_val]"}

    print("-------------------------------------------")
    print(server_ip)

    # Set the address and make images call to get the cookies
    # We don't actually do anything with this call other than get cookies and check Karbon Version
    url = "https://"+server_ip+":9440/api/nutanix/v3/groups"
    try:
        resp = requests.post(url, data=json.dumps(payload), headers=headers, auth=(pc_user, pc_pass), verify=False,timeout=10)
        # If the call went through successfully
        if resp.ok:
            # Set the cookie so we can move forward to Karbon
            #print("COOKIES={0}".format(resp.cookies['NTNX_IGW_SESSION']))
            cookies = {'NTNX_IGW_SESSION': resp.cookies['NTNX_IGW_SESSION']}
            resp_json=json.loads(resp.content)

            # Trying to get the version of Karbon before we move on
            count=0
            count1=0
            count2=0
            karbon_ver=0
            # Loop through the outer loop of group_results
            while count < len(resp_json['group_results']):
                # Loop through the entity_results array
                while count1 < len(resp_json['group_results'][count]['entity_results']):
                    # Loop through the data results
                    while count2 < len(resp_json['group_results'][count]['entity_results'][count1]['data']):
                        if resp_json['group_results'][count]['entity_results'][count1]['data'][count2]['name'] == "entity_model":
                            if resp_json['group_results'][count]['entity_results'][count1]['data'][count2]['values'][0]['values'][0]=="Karbon":
                                karbon_ver=resp_json['group_results'][count]['entity_results'][count1]['data'][count2+1]['values'][0]['values'][0]
                        count2+=1

                    count1+=1
                    count2=0

                count+=1
                count1=0

            # Now if we have found Karbon 2.0.0 we can proceed. Otherwise break and move on to the next, but let people know..
            if str(karbon_ver)=="2.0.0":

                # Open the connection to the Karbon server before moving on...
                url = "https://" + server_ip + ":7050/karbon/acs/image/portal/list"
                try:
                    resp = requests.get(url, cookies=cookies, headers=headers, verify=False, timeout=10)
                    if not "html" in str(resp.content):
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

                    else:
                        print("Error occured in the retrieval of Karbon. Has it been started??")

                except requests.exceptions.RequestException as err:
                    print("OOps Error: Something Else", err)
                except requests.exceptions.HTTPError as errh:
                    print("Http Error:", errh)
                except requests.exceptions.ConnectionError as errc:
                    print("Error Connecting:", errc)
                except requests.exceptions.Timeout as errt:
                    print("Timeout Error:", errt)
                    print("We are unable to get to the Karbon Server.....")
            else:
                print("We have found a wrong version of karbon. We found version "+str(karbon_ver)+". PLease check that LCMhas run on the PRISM Central!!...")

    # If we made it this far, the nutanix/image/list call failed
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


# ---------- Main ---------------------

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
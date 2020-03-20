import requests
import json
import urllib3
import sys

#####################################################################################################################################################################
# Check routine to see if the cluster is available
#####################################################################################################################################################################
def check_avaialbility(ip_address,user,passwd):
    # Get the URL and compose the command to get the request from the REST API of the cluster
    url = "https://" + ip_address + ":9440/PrismGateway/services/rest/v1/eulas"
    header_post = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    print("Checking availability on "+ip_address)
    try:
        page = requests.get(url, verify=False, auth=(user, passwd))
        page.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps Error: Something Else", err)
        return
    except requests.exceptions.HTTPError as errh:
        print("Http Error")
        return
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting")
        return
    except requests.exceptions.Timeout as errt:
        print("Timeout Error")
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
    line_dict=line.split("|")
    server_ip_var=line_dict[0]
    user_name='admin'
    passwd_var=line_dict[1]
    check_avaialbility(server_ip_var,user_name,passwd_var)
    print('--------------------------------')


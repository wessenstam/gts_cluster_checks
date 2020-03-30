# cluster_checks
Python scripts to test the clusters after they have been deployed

Usage
=====

Running the python3 script use a file ``cluster.txt`` that needs to hold three variables. The file has the same settings as in the cluster.txt file we use for the stage_workshop mass deploy<BR>
The file needs to look like:
``IPADDRESS|<ADMIN_PASSWORD>|EMAILADDRESS`` example: ``10.10.10.37|techTest!@#|bogus@nutanix.comt``

The easiest way is to use the file that is being used for the staging of the clusters in HPOC.

manipulate_cluster.py
---------------------
If the file is not in the correct format you can use the ``python3 manipulate_cluster.py``. it will add the needed information to the list of IP addresses.
Make sure the cluster.txt file has the ip addresses and the script will add ``|password|emailaddress`` to each line at the end. This file can then be used for the deployment of the clusters.

PRISM Elements
--------------
Use ``python3 cluster_pe.py`` to check the settings for the PE environment:<BR>
a) Eula<BR>
b) Pulse<BR>
c) Network<BR>
  1. Right networks?<BR>
  2. Right VLANs?<BR>
  
d) is AD configured<BR>
e) DNS servers<BR>
f) NTP servers<BR>

PRISM Central
-------------
Use ``python3 cluster_pc.py`` to check for the PC environment:<BR>
a) DNS servers<BR>
b) is AD integrated<BR>
c) is Calm enabled<BR>
d) is Karbon enabled<BR>
e) is Objects enabled<BR>
f) has LCM run adn updated the components<BR>
g) has Flow been enabled<BR>
h) do we have the blueprints? We check:

    1) CICD
    2) Citrix
    3) Era deployment
    4) KarbonClusterDeployment

i) Are the apps running?<br>
j) Do we have the images uploaded? If not which are missing?<BR>

Apps check
----------
Use ``python3 cluster_bp.py`` to check for the PC environment:<BR>
a) Are the apps running? We check:

    1) Citrix Infra
    2) Era Server
    3) KarbonClusterDeployment
    
Force Karbon image download
----------------
Sometimes the Karbon BP isn't able to download the Karbon Image. To force the Karbon image to download use this script. I uses the information from the cluster.txt file. Run using ``python3 karbon_download.py``. This will check for the image ntnx-04 available. If not it tells Karbon to download the image.

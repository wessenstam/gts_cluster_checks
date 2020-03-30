file_name = "cluster.txt"
string_to_add = "|emeaX2020!|willem@nutanix.com"

with open(file_name, 'r') as f:
    file_lines = [''.join([x.strip(), string_to_add, '\n']) for x in f.readlines()]

with open(file_name, 'w') as f:
    f.writelines(file_lines)
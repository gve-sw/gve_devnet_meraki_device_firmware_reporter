""" Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

import meraki
import config
import pprint
import csv
from datetime import datetime


tocsv = []
dashboard = meraki.DashboardAPI(config.key,single_request_timeout=999999,output_log=False,print_console=False)
orgs = dashboard.organizations.getOrganizations()

for org in orgs:
    networks = dashboard.organizations.getOrganizationNetworks(organizationId=org['id'])
    for network in networks:
        try:
            firmwares = dashboard.networks.getNetworkFirmwareUpgrades(networkId=network['id'])
        except Exception as e: 
            print(e)
            continue
        try:
            devices = dashboard.networks.getNetworkDevices(network["id"])
            for device in devices:
                if device['model'].startswith('MS') or device['model'].startswith('MR'):
                    temp = {}
                    if 'name' in device:
                        temp['Hostname'] = device['name']
                    else:
                        temp['Hostname'] = 'N/A'
                    temp['System IP'] = device['lanIp']
                    temp['Device Model'] = device['model']
                    temp['Current Version'] = device['firmware']
                    temp['Default Version'] = 'N/A'
                    
                    if device['model'].startswith('MS'):
                        for index,firmware in enumerate(firmwares['products']['switch']['availableVersions']):
                            if firmware['releaseType'] == 'stable':
                                if index == 0:
                                    temp['Default Version'] = firmware['firmware']

                    if device['model'].startswith('MR'):
                        for index,firmware in enumerate(firmwares['products']['wireless']['availableVersions']):
                            if firmware['releaseType'] == 'stable':
                                if index == 0:
                                    temp['Default Version'] = firmware['firmware']

                tocsv.append(temp)
        except Exception as e: 
            print(e)
            continue

headerList = ['Hostname','System IP','Device Model','Current Version','Default Version']

with open('report.csv','w',encoding='utf8',newline='') as output_file:
    fc = csv.DictWriter(output_file,fieldnames=headerList,)
    fc.writeheader()
    fc.writerows(tocsv)
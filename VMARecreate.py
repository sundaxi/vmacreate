#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 11/22/2017 8:47 PM
# @Author  : Ying Sun
# @Link    : yinsun@microsoft.com
# @Version : 0.1

import json
import subprocess
import sys
import os

## variables defination
_availabilitySet = "availabilitySet"
_hardwareProfile = "hardwareProfile"
_vmSize = "vmSize"
_id = "id"
_name = "name"
_networkProfile = "networkProfile"
_networkInterfaces = "networkInterfaces"
_resourceGroup = "resourceGroup"
_resources = "resources"
_location = "location"
_storageProfile = "storageProfile"
_osDisk = "osDisk"
_managedDisk = "managedDisk"
_osType = "osType"
_vhd = "vhd"
_uri = "uri"
_virtualMachine = "virtualMachine"
_network = "network"
_publicIpAddresses = "publicIpAddresses"

## Define command line
az_vm_list = "az vm list -o table"

class AzCmd(object):
    def __init__(self):
        pass

    def AzVmList(self,cmd):
        self.az_vm_list = subprocess.getstatusoutput(cmd)
        return self.az_vm_list

    def AzVmShow(self,cmd):
        self.az_vm_show = subprocess.check_output(cmd,shell=True)
        return self.az_vm_show

class SelectVm(object):
    def __init__(self,azobj):
        self.vmname = ''
        self.rgname = ''
        self.azobj = azobj

    def ShowTable(self):
        try:
            while True:
                title = """
Here are two methods below:
1). Show all your VMs and select
2). Input your vm and resourcegroup"""
                print(title)
                option = input("\033[32mPlease choose: \033[0m")
                if option.strip() == "1":
                    self.Method = "SelectTable"
                    self.cmd_output = self.azobj.AzVmList(az_vm_list)
                elif option.strip() == "2":
                    self.Method = "InputTable"
                else:
                    print("\033[31mWrong Input\033[0m")
                    continue
                break
        except Exception as e:
            print("Error Input",e)
            sys.exit(2)

    def SelectTable(self):
        Flag = False
        while not Flag:
            count = -2
            for i in self.cmd_output[1].split('\n'):
                count += 1
                if count == -1:
                    continue
                elif count == 0:
                    print("%4s: %-30s %-30s" % (" Num", "Vmname", "RgName"))
                    continue
                # print(count,": ",i.split()[0],"\t\t\t\t",i.split()[1])
                print("%4s: %-30s %-30s" % (count, i.split()[0], i.split()[1]))
            num = input('Please input your vm: ')
            try:
                if int(num) < count:
                    Flag = True
                    count_inner = -1
                    for j in self.cmd_output[1].split('\n'):
                        if int(num) == count_inner:
                            self.vmname = j.split()[0]
                            self.rgname = j.split()[1]
                        count_inner += 1
            except Exception as e:
                print("Invalid input")

        cmd_az_show_vm = "az vm show -g %s -n %s" % (self.rgname, self.vmname)
        cmd_az_list_ip_addresses = "az vm list-ip-addresses -g %s -n %s" % (self.rgname,self.vmname)
        return cmd_az_show_vm, cmd_az_list_ip_addresses

    def InputTable(self):
        self.vmname = input("Please input the name of your VirtualMachine: ")
        self.rgname = input("Please input the name or your ResourceGroup: ")
        cmd_az_show_vm = "az vm show -g %s -n %s" % (self.rgname, self.vmname)
        cmd_az_list_ip_addresses = "az vm list-ip-addresses -g %s -n %s" % (self.rgname, self.vmname)

        cmd_az_show_vm = "az vm show -g %s -n %s" % (self.rgname, self.vmname)
        cmd_az_list_ip_addresses = "az vm list-ip-addresses -g %s -n %s" % (self.rgname,self.vmname)
        return cmd_az_show_vm,cmd_az_list_ip_addresses

    def DeleteVM(self):
        delete_vm_cmd = "az vm delete -n %s -g %s" % (self.vmname, self.rgname)
        return delete_vm_cmd

class Tools(object):
    def __init__(self):
        pass

    def GetNics(self,vm_nics_list):
        nics_list = []
        for nic in vm_nics_list:
            nics_list.append(nic[_id].split("/")[-1])
        nics_list.reverse()
        vm_nics = ""
        for nic in nics_list:
            vm_nics = nic + " " + vm_nics
        return vm_nics

    def GetPublicIp(self,az_list_ip_addresses_list_json,vm_resourcegroup):
        Flag = False
        for vm_publicIps in az_list_ip_addresses_list_json:
            if len(vm_publicIps[_virtualMachine][_network][_publicIpAddresses]) == 0:
                continue
            vm_publicIp = vm_publicIps[_virtualMachine][_network][_publicIpAddresses][0][_id].split("/")[-1]
            if Flag is not True:
                Flag = True
            cmd = "az network public-ip update --resource-group %s --name %s --allocation-method Static" % (
            vm_resourcegroup, vm_publicIp)
            return cmd

    def Print(self,delete_vm_cmd, az_cmd_generated,allocate_static_public_ip):
        output_final = """
Thanks for your patience 
\033[33m1. You can use this command to delete your virtual machine and keep your osDisk 
\033[31m%s 
\033[33m2. You can use this command to allocate your current Public IP address as static 
\033[31m%s 
\033[33m3. You can use this command to re-create your vm after your change 
\033[31m%s\033[0m      
""" % (delete_vm_cmd, az_cmd_generated,allocate_static_public_ip)
        print(output_final)

class GetParmeters(object):
    def __init__(self, az_show_vm_json,Tool):
        self.vm_size = az_show_vm_json[_hardwareProfile][_vmSize]
        self.vm_location = az_show_vm_json[_location]
        self.vm_name = az_show_vm_json[_name]
        self.vm_resourcegroup = az_show_vm_json[_resourceGroup]
        self.vm_nics_list = az_show_vm_json[_networkProfile][_networkInterfaces]
        self.vm_nics = Tool.GetNics(self.vm_nics_list)
        self.vm_os_type = az_show_vm_json[_storageProfile][_osDisk][_osType]

        if az_show_vm_json[_availabilitySet] is not None:
            self.vm_availability_set = az_show_vm_json[_availabilitySet][_id].split("/")[-1]
        else:
            self.vm_availability_set = None

    def GetParmeters(self):
        if az_show_vm_json[_storageProfile][_osDisk].get(_managedDisk) is not None:
            print("\033[31mthis is managed disk\033[0m")
            __disktype = "managed"
            vm_os_disk = az_show_vm_json[_storageProfile][_osDisk][_name]
            if self.vm_availability_set is not None:
                az_cmd_generated = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk, self.vm_availability_set)
            else:
                az_cmd_generated = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk)

        else:
            print("\033[32mthis is umanaged disk\033[0m")
            __disktype = "umanaged"
            vm_vhd = az_show_vm_json[_storageProfile][_osDisk][_vhd][_uri]
            if self.vm_availability_set is not None:
                az_cmd_generated = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_vhd)
            else:
                az_cmd_generated = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_vhd, self.vm_availability_set)
        print("\033[32mRunning... It will take several secs...\033[0m")
        return az_cmd_generated

if __name__ == '__main__':
    # initiate  object
    try:
        az_obj = AzCmd()
        select_obj = SelectVm(az_obj)
        Tool = Tools()
        select_obj.ShowTable()
        if hasattr(select_obj,select_obj.Method):
            Table = getattr(select_obj,select_obj.Method)
        cmd_az_show_vm, cmd_az_list_ip_addresses = Table()

        # cmd_az_show_vm, cmd_az_list_ip_addresses = SelectVm().SelectTable(cmd_output)
        az_show_vm = az_obj.AzVmShow(cmd_az_show_vm)

        if len(az_show_vm) == 0:
            print("\033[31mError...No such vm in this subscription!\033[0m")
            sys.exit(2)
        az_list_ip_addresses_list = az_obj.AzVmShow(cmd_az_list_ip_addresses)

        # deserialization az show -n vmaname -g rgname
        az_show_vm_json = json.loads(az_show_vm)
        # deserialization az vm list-ip-addresses -g rgname -n vmname
        az_list_ip_addresses_list_json = json.loads(az_list_ip_addresses_list)
        vm_paramters = GetParmeters(az_show_vm_json,Tool)
        az_cmd_generated = vm_paramters.GetParmeters()
        allocate_static_public_ip = Tool.GetPublicIp(az_list_ip_addresses_list_json,vm_paramters.vm_resourcegroup)
        Tool.Print(select_obj.DeleteVM(),allocate_static_public_ip,az_cmd_generated)
    except Exception as e:
        print("Unexpected error!",e)




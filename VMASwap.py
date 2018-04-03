#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 4/3/2018 12:00 PM
# @Author  : Ying Sun
# @Link    : yinsun@microsoft.com
# @Version : 0.1

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 11/22/2017 8:47 PM
# @Author  : Ying Sun
# @Link    : yinsun@microsoft.com
# @Version : 0.1

import json
import subprocess
import sys
import os
import datetime
import time


# az storage container create -n newvhd --account-name yingresourcegroupasia
# az storage blob copy start -u https://yingresourcegroupasia.blob.core.windows.net/vhds/yingrhel6820170810094319.vhd -b new.vhd -c newvhd --account-name yingresourcegroupasia

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
_diagnosticsProfile = "diagnosticsProfile"
_storageUri = "storageUri"
_bootDiagnostics = "bootDiagnostics"
_encryptionSettings = "encryptionSettings"
_diskEncryptionKey = "diskEncryptionKey"
_keyEncryptionKey = "keyEncryptionKey"
_storageAccountType = "storageAccountType"
_offer = "offer"
_publisher = "publisher"
_sku = "sku"
_version = "version"
_imageReference = "imageReference"
_dataDisks = "dataDisks"
_caching = "caching"
_settings = "settings"
_AADClientID = "AADClientID"
_KeyEncryptionKeyURL = "KeyEncryptionKeyURL"
_KeyVaultURL = "KeyVaultURL"
_VolumeType = "VolumeType"

datename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
temptime = datetime.datetime.now().strftime("%Y%m%d")

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
                option = input("\033[32mPlease choose[num]: \033[0m")
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
            num = input('Please choose your virtual machine [num]: ')
            try:
                if int(num) <= count:
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

    def EnableDiagnostics(self,az_list_ip_address):
    #     az vm boot-diagnostics enable --name --resource-group --storage
        pass

    def Print(self,*args):
        output_final = """
Thanks for your patience 
\033[33m1.Firstly, backup your vhd. The backup vhd will be used for further troubleshooting 
\033[36m%s
\033[33m2.Deallocate the virtual machine  
\033[36m%s
\033[33m3.Create temporary troubleshooting virtual machine (for Premium vm, please use vm size Standard_DS1_v2)
\033[36m%s
\033[33m4.Attach the issued OS disk to the troubleshooting vm
\033[36m%s
\033[33m5.After troubleshooting, detach the issued os disk from troubleshooting vm 
\033[36m%s
\033[33m6.Swap the modified os disk to the existing vm.
\033[36m%s
\033[0m    
""" % (args)
        with open('operation_' + vm_paramters.vm_name + '.log','w+',encoding='utf8') as f:
            f.write(output_final)
        print(output_final)
    def PrintEncrption(self,*args):
        output_final = """
Thanks for your patience 
This is an Encrypted virtual machine. Please follow below procedure to troubleshoot the issued virutal machine 
\033[33m1.Firstly, backup your vhd. You could ether moidfy the OS disk directly or modify the backup vhd
\033[36m%s
\033[33m2.Deallocate the virtual machine 
\033[36m%s
\033[33m3.Create temporary troubleshooting virtual machine (for Premium disk, please use vm size Standard_DS1_v2)
\033[36m%s
\033[33m4.Enable encryption settigns on troubleshooting vm and disable encryption settings on the issued os Disk(managed disk only)
\033[36m%s
\033[33m5.Attach the copied issued OS disk to the troubleshooting vm
\033[36m%s
//Linux commnad reference, suppose /dev/sdc1 is the bek key and /dev/sdd is the issued os disk 
mkdir /{investigatekey,investigateboot,investigateroot}
mount /dev/sdc1 /investigatekey 
mount -o nouuid /dev/sdd1 /investigateboot 
cryptsetup luksOpen --key-file /investigatekey/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader /dev/sdd2 investigateosencrypt
mount -o nouuid /dev/mapper/investigateosencrypt /investigateroot
\033[33m6.After troubleshooting, detach the issued os disk from troubleshooting vm 
\033[36m%s
\033[33m7.Update the encryption settings back to the copied vhd 
\033[36m%s
\033[33m8.Use swap API to swap the os disk back 
\033[36m%s 
\033[0m
""" % (args)
        print(output_final)
        with open('operation_' + vm_paramters.vm_name + '.log' ,'w+',encoding='utf8') as f:
            f.write(output_final)


class GetParmeters(object):
    def __init__(self, az_show_vm_json,Tool):
        self.vm_size = az_show_vm_json[_hardwareProfile][_vmSize]
        self.vm_location = az_show_vm_json[_location]
        self.vm_name = az_show_vm_json[_name]
        self.vm_resourcegroup = az_show_vm_json[_resourceGroup]
        self.vm_nics_list = az_show_vm_json[_networkProfile][_networkInterfaces]
        self.vm_nics = Tool.GetNics(self.vm_nics_list)
        self.vm_os_type = az_show_vm_json[_storageProfile][_osDisk][_osType]
        self.vm_image_reference = az_show_vm_json[_storageProfile][_imageReference]
        self.vm_temp_name = "temp" + temptime
        self.vm_os_datadisk_list = az_show_vm_json[_storageProfile][_dataDisks]
        if self.vm_image_reference is not None:
            self.vm_image = "%s:%s:%s:%s" % (self.vm_image_reference[_publisher],self.vm_image_reference[_offer],self.vm_image_reference[_sku],self.vm_image_reference[_version])
        else:
            self.vm_image = "<publisher:offer:sku:version>ex\\RedHat:RHEL:7.3:latest"
        if az_show_vm_json[_storageProfile][_osDisk][_encryptionSettings] is not None:
            self.vm_diskEncryptionKey = az_show_vm_json[_storageProfile][_osDisk][_encryptionSettings][_diskEncryptionKey]
            self.vm_keyEncryptionKey = az_show_vm_json[_storageProfile][_osDisk][_encryptionSettings][_keyEncryptionKey]
            vm_os_disk = az_show_vm_json[_storageProfile][_osDisk][_name]
            self.disable_disk_encryption_setings = "az disk update -n %s -g %s --set encryptionSettings.enabled=false encryptionSettings.diskEncryptionKey=null encryptionSettings.keyEncryptionKey=null" % (vm_os_disk + "-copy", self.vm_resourcegroup)
            self.enable_disk_encryption_settings = 'az disk update -n %s -g %s --set encryptionSettings.enabled=true encryptionSettings.diskEncryptionKey="%s" encryptionSettings.keyEncryptionKey="%s"' % (vm_os_disk + '-copy', self.vm_resourcegroup,self.vm_diskEncryptionKey,self.vm_keyEncryptionKey)
            self.enable_encryption_settings_temp = 'az vm update -n %s -g %s --set storageProfile.osDisk.encryptionSettings.diskEncryptionKey="%s" storageProfile.osDisk.encryptionSettings.keyEncryptionKey="%s" storageProfile.osDisk.encryptionSettings.Enabled=true ' % (self.vm_temp_name,self.vm_resourcegroup,
            self.vm_diskEncryptionKey, self.vm_keyEncryptionKey)

            self.enable_encryption_settings_vm_cmd = 'az vm update -n %s -g %s --set storageProfile.osDisk.encryptionSettings.diskEncryptionKey="%s" storageProfile.osDisk.encryptionSettings.keyEncryptionKey="%s" storageProfile.osDisk.encryptionSettings.Enabled=true ' % (self.vm_name,self.vm_resourcegroup,
            self.vm_diskEncryptionKey, self.vm_keyEncryptionKey)


            self.encryption = "True"
            self.resources_list = az_show_vm_json[_resources]
            for resources in self.resources_list:
                if resources[_name] == "AzureDiskEncryptionForLinux":
                    self.keyvault = resources[_settings][_KeyVaultURL].split('https://')[1].split(".vault.azure.net")[0]
                    self.key = resources[_settings][_KeyEncryptionKeyURL].split("/keys/")[1].split("/")[0]
                    self.aadclientid = resources[_settings][_AADClientID]
                    self.encryption_volumetype = resources[_settings][_VolumeType]
            # define az vm encryption command
            self.az_vm_encryption_enable_cmd = "az vm encryption enable --resource-group %s --name %s --aad-client-id %s --aad-client-secret %s --disk-encryption-keyvault %s --key-encryption-key %s --volume-type %s" % (self.vm_resourcegroup,self.vm_name,self.aadclientid,"<Service Principal password>",self.keyvault,self.key, self.encryption_volumetype)
            # define az ad sp reset-credentials command
            self.az_ad_sp_reset_credential_cmd = "az ad sp reset-credentials --name %s --password %s" % (self.aadclientid,"<Service Principal Password>")

        else:
            self.enable_encryption_settings_temp = 'No encryption settings'
            self.encryption = "False"
        if az_show_vm_json[_diagnosticsProfile] is not None:
            self.vm_storageURI= az_show_vm_json[_diagnosticsProfile][_bootDiagnostics][_storageUri]
        else:
            self.vm_storageURI = "<StorageURI>"
        if az_show_vm_json[_availabilitySet] is not None:
            self.vm_availability_set = az_show_vm_json[_availabilitySet][_id].split("/")[-1]
        else:
            self.vm_availability_set = None

    def GetParmeters(self):
        az_vm_attach_data_disk_cmd = ""
        az_vm_deallocate_cmd = 'az vm stop -g %s -n %s' % (self.vm_resourcegroup, self.vm_name)
        if az_show_vm_json[_storageProfile][_osDisk].get(_managedDisk) is not None:
            print("\033[33mthis is managed disk\033[0m")
            __disktype = "managed"
            vm_os_disk = az_show_vm_json[_storageProfile][_osDisk][_name]
            vm_os_disk_storageAccountType = az_show_vm_json[_storageProfile][_osDisk][_managedDisk][_storageAccountType]
            vm_os_disk_snapshot = vm_os_disk + '-snapshot'
            az_snapshot_create = "az snapshot create -g %s --source %s --name %s" % (self.vm_resourcegroup,vm_os_disk,vm_os_disk_snapshot)
            az_disk_create = "az disk create --resource-group %s --source %s --name %s --sku %s" %(self.vm_resourcegroup,vm_os_disk_snapshot,vm_os_disk+"-copy",vm_os_disk_storageAccountType)
            az_backup_cmd = az_snapshot_create + "\n" + "//Create new disk" + "\n" + az_disk_create

            managedDisk_id = az_show_vm_json[_storageProfile][_osDisk][_managedDisk][_id]
            swap_managedDisk_id = managedDisk_id.replace(vm_os_disk, vm_os_disk + "-copy")
            # az vm create  -g encryption --image "RedHat:RHEL:7.3:latest --admin-username azureuser --admin-password Azuretroubleshoot123! --name temp20180302 --size Standard_A1
            az_temp_vm_attach_disk_cmd = "az vm disk attach --disk %s --resource-group %s --vm-name %s" % (vm_os_disk + "-copy",self.vm_resourcegroup,self.vm_temp_name)
            az_temp_vm_detach_disk_cmd = "az vm disk detach -g %s --vm-name %s -n %s" % (self.vm_resourcegroup,self.vm_temp_name,vm_os_disk + '-copy')
            az_swap_disk_cmd = 'az feature register --namespace "microsoft.compute" -n "AllowManagedDisksReplaceOSDisk"\n' + "az provider register -n microsoft.compute\n" + "az vm update --name %s --resource-group %s --os-disk %s" %(self.vm_name,self.vm_resourcegroup,swap_managedDisk_id)

            if len(self.vm_os_datadisk_list) > 0:
                count_lun = len(self.vm_os_datadisk_list) - 1
                self.vm_os_datadisk_list.reverse()
                for datadisk in self.vm_os_datadisk_list:
                    if datadisk[_caching] is None:
                        data_caching = "None"
                    data_caching = datadisk[_caching]
                    az_vm_attach_data_disk = "az vm disk attach --disk %s --resource-group %s --vm-name %s --caching %s --lun %s\n" % (datadisk[_managedDisk][_id].split("/")[-1], self.vm_resourcegroup, self.vm_name, data_caching, str(count_lun))
                    az_vm_attach_data_disk_cmd = az_vm_attach_data_disk + az_vm_attach_data_disk_cmd
                    count_lun -= 1
            else:
                az_vm_attach_data_disk_cmd = "No data disk"

            az_vm_create_temp_cmd = "az vm create -g %s --image %s --admin-username azureuser --admin-password Azuretroubleshooting123! --name %s --size Standard_A1" % (self.vm_resourcegroup, self.vm_image, self.vm_temp_name)
            if self.vm_availability_set is not None:
                az_cmd_generated1 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk, self.vm_availability_set)
                az_cmd_generated2 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk+"-copy", self.vm_availability_set)
            else:
                az_cmd_generated1 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk)
                az_cmd_generated2 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_os_disk+"-copy")
            if self.encryption == "True":
                self.enable_encryption_settings_temp = self.enable_encryption_settings_temp + "\n//Remove encryption settings on issued os disk\n" + self.disable_disk_encryption_setings
        else:
            print("\033[33mthis is unmanaged disk\033[0m")
            __disktype = "unmanaged"
            vm_vhd = az_show_vm_json[_storageProfile][_osDisk][_vhd][_uri]
            storageaccount = vm_vhd.split(".blob")[0].split("https://")[1]
            storageaccount_uri = "https://" + vm_vhd.split("https://")[1].split('/')[0]
            vhd_name = vm_vhd.split("/")[-1]
            vhd_backup_name = vhd_name.split(".vhd")[0] + "_bak.vhd"
            az_storage_container_create = "az storage container create -n %s --account-name %s" % (datename, storageaccount)
            az_storage_blob_copy = "az storage blob copy start -u %s -b %s -c %s --account-name %s" %(vm_vhd, vhd_backup_name,datename,storageaccount)
            az_bak_disk_uri = storageaccount_uri + "/" + datename + "/" + vhd_backup_name
            print("az_bak_disk_uri",az_bak_disk_uri)
            az_backup_cmd = az_storage_container_create + "\n" + az_storage_blob_copy
            # az vm create -g encryption --image "RedHat:RHEL:7.3:latest"  --admin-username azuretroubleshoot --admin-password Azuretroulbeshoot123! --name troubleshootvm20180303 --use-unmanaged-disk --storage-account encrption --storage-sku Standard_LRS

            az_vm_create_temp_cmd = "az vm create -g %s --image %s --admin-username azureuser --admin-password Azuretrouleshooting123! --name %s --use-unmanaged-disk --storage-account %s --size Standard_A1" % (self.vm_resourcegroup, self.vm_image, self.vm_temp_name, storageaccount)
            az_temp_vm_attach_disk_cmd = "az vm unmanaged-disk attach --resource-group %s --vm-name %s --vhd-uri %s -n %s" % (self.vm_resourcegroup, self.vm_temp_name, az_bak_disk_uri ,vhd_backup_name.split(".vhd")[0])
            az_temp_vm_detach_disk_cmd = "az vm unmanaged-disk detach -g %s --vm-name %s -n %s" % (self.vm_resourcegroup,self.vm_temp_name,vhd_backup_name.split(".vhd")[0])
            az_swap_disk_cmd = "az vm update -g %s -n %s --set StorageProfile.OsDisk.Vhd.Uri=%s" % (self.vm_resourcegroup,self.vm_name,az_bak_disk_uri)

            if len(self.vm_os_datadisk_list) > 0:
                self.vm_os_datadisk_list.reverse()
                for datadisk in self.vm_os_datadisk_list:
                    count_lun = len(self.vm_os_datadisk_list) - 1
                    if datadisk[_caching] is None:
                        data_caching = "None"
                    data_caching = datadisk[_caching]
                    az_vm_attach_data_disk = "az vm unmanaged-disk attach --resource-group %s --vm-name %s --vhd-uri %s -n %s --lun %s --caching %s\n" % (self.vm_resourcegroup,self.vm_name, datadisk[_vhd][_uri], datadisk[_vhd][_uri].split("/")[-1].split('.vhd')[0],str(count_lun),data_caching)
                    az_vm_attach_data_disk_cmd = az_vm_attach_data_disk + az_vm_attach_data_disk_cmd
                    count_lun -= 1
            else:
                az_vm_attach_data_disk_cmd = "No data disk"

            if self.vm_availability_set is not None:
                az_cmd_generated1 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_vhd, self.vm_availability_set)
                az_cmd_generated2 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s --availability-set %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, az_bak_disk_uri, self.vm_availability_set)

            else:
                az_cmd_generated1 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, vm_vhd)
                az_cmd_generated2 = "az vm create --name %s --resource-group %s --location %s --nics %s --size %s --os-type %s --use-unmanaged-disk --attach-os-disk %s" % (
                    self.vm_name, self.vm_resourcegroup, self.vm_location, self.vm_nics, self.vm_size,
                    self.vm_os_type, az_bak_disk_uri)
        # az_cmd_generated = "//Recreate vm based on original vhd\n" + az_cmd_generated1 + "\n//Recreate vm base on new created vhd\n" + az_cmd_generated2
        # //Recreate vm based on original vhd\n
        az_cmd_generated = az_cmd_generated1
        return az_cmd_generated, az_backup_cmd, az_vm_create_temp_cmd, az_temp_vm_attach_disk_cmd, az_temp_vm_detach_disk_cmd, az_vm_attach_data_disk_cmd,az_swap_disk_cmd,az_vm_deallocate_cmd

if __name__ == '__main__':
#     # initiate  object
#     try:
        command_list = []
        az_obj = AzCmd()
        select_obj = SelectVm(az_obj)
        Tool = Tools()
        select_obj.ShowTable()
        if hasattr(select_obj,select_obj.Method):
            Table = getattr(select_obj,select_obj.Method)
        cmd_az_show_vm, cmd_az_list_ip_addresses = Table()

        # cmd_az_show_vm, cmd_az_list_ip_addresses = SelectVm().SelectTable(cmd_output)
        print("\033[32mRunning... It will take few secs...\033[0m")
        az_show_vm = az_obj.AzVmShow(cmd_az_show_vm)


        if len(az_show_vm) == 0:
            print("\033[31mError...No such vm in this subscription!\033[0m")
            sys.exit(2)
        az_list_ip_addresses_list = az_obj.AzVmShow(cmd_az_list_ip_addresses)

        # deserialization az show -n vmaname -g rgname
        az_show_vm_json = json.loads(az_show_vm.decode())
        # deserialization az vm list-ip-addresses -g rgname -n vmname
        az_list_ip_addresses_list_json = json.loads(az_list_ip_addresses_list.decode())
        vm_paramters = GetParmeters(az_show_vm_json,Tool)
        az_cmd_generated, az_backup_cmd, az_vm_create_temp_cmd,az_temp_vm_attach_disk_cmd,az_temp_vm_detach_disk_cmd, az_vm_attach_data_disk_cmd,az_swap_disk_cmd, az_vm_deallocate_cmd = vm_paramters.GetParmeters()
        allocate_static_public_ip = Tool.GetPublicIp(az_list_ip_addresses_list_json,vm_paramters.vm_resourcegroup)
        enable_boot_diagnostics = "az vm boot-diagnostics enable --name %s --resource-group %s --storage %s" % (vm_paramters.vm_name,vm_paramters.vm_resourcegroup,vm_paramters.vm_storageURI)
        with open('GetVm' + vm_paramters.vm_name + '.json','w+',encoding='utf8') as f:
            f.write(str(az_show_vm,encoding='utf-8'))

        if vm_paramters.encryption == "True":
            Tool.PrintEncrption(az_backup_cmd,az_vm_deallocate_cmd,az_vm_create_temp_cmd,vm_paramters.enable_encryption_settings_temp,az_temp_vm_attach_disk_cmd,az_temp_vm_detach_disk_cmd, vm_paramters.enable_disk_encryption_settings,az_swap_disk_cmd)
        else:
            Tool.Print(az_backup_cmd,az_vm_deallocate_cmd,az_vm_create_temp_cmd,az_temp_vm_attach_disk_cmd,az_temp_vm_detach_disk_cmd,az_swap_disk_cmd)
    # except Exception as e:
    #     print("Unexpected error!",e)




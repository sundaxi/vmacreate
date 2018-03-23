# VMArecreate_tool.md

Table of Contents
=================
- [VMArecreate_tool.md](#vmarecreate-toolmd)
- [Table of Contents](#table-of-contents)
  * [Introduction](#introduction)
  * [How to Start](#how-to-start)
  * [Get started](#get-started)
    + [For Option 1](#for-option-1)
    + [For Option 2](#for-option-2)
  * [Troubleshooting](#troubleshooting)
    + [Normal Virtual Machine without encryption](#normal-virtual-machine-without-encryption)
      - [Managed disk](#managed-disk)
    + [unmanaged disk](#unmanaged-disk)
    + [Encrypted Virtual Machine](#encrypted-virtual-machine)
    + [Supplement](#supplement)
  * [Contact](#contact)

## Introduction 

This tool is used to troubleshoot azure ARM virtual machine(v2). You can use this tool to delete and rebuild your virtual machine easily. 

## How to Start 

Login to Azure portal via https://portal.azure.com 
And click the button to use Azure Cloud Shell ![cloud_shell.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/cloud_shell.png?raw=true)
Select your subscription and login to Azure cloud shell![cloud_shell_login.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/cloud_shell_login.png?raw=true)

If you didn't select the correct subscription, please set your subscription 

```shell
az account set -s <subscription_id> 
```

Clone the code from github

```shell
git clone https://github.com/sundaxi/vmacreate.git
cd vmacreate/
```

Run the command 

```shell 
./VMARecreate.py
```

The script will prompted you two options 

-   You can list all the VMs and select the case from the list 
-   You can also input the name and resourcegroup of the virtual machine 

## Get started 

There are two options avaliable

### For Option 1

list all the vm and select

![show_all_vm.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/show_all_vm.png?raw=true)

Select your issued VMs by Num and the command will get accordingly ![command_output.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/command_output.png?raw=true)

### For Option 2

Input your the name and resourcegroup of your virtual machine. 

![option2.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/option2.png?raw=true)

## Troubleshooting

In Azure, sometimes we have to use chroot method to troubleshoot the issued virtual machine just like the rescue mode in on-prem envrionment. Refer to [chroot][https://blogs.msdn.microsoft.com/linuxonazure/2016/08/16/linux-recovery-using-chroot-steps-to-recover-vms-that-are-not-accessible/]

### Normal Virtual Machine without encryption 

Please follow the instruction to run the VMAReceate script from Azure Cloud Shell.
The script will generate all the command for you automatically. Here coms the example for you to do the troubleshooting 

#### Managed disk  

Backup your vhd. For managed disk you need to create a snapshot for backup purpose and you could create a cloned VHD from the snapshot

```bash
az snapshot create -g development --source d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000 --name d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000-snapshot
//Create new disk
az disk create --resource-group development --source d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000-snapshot --name d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000-c
opy --sku Standard_LRS
```

Create Snapshot![create_snapshot.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/create_snapshot.png?raw=true)
Create vhd from snapshot ![create_vhd_from_snapshot.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/create_vhd_from_snapshot.png?raw=true)

(Optional) You can allocate the public IP as static if you want to keep the IP address

```shell
az network public-ip update --resource-group development --name pyclient-ip --allocation-method Static
```

![allocate_static_IP_managedisk.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/allocate_static_IP_managedisk.png?raw=true)

Delete the Virtual Machine, this proecedure only delete the Virtual Machine Instance and all your resources like VHD, NICs, Availablity-Set will keep 

```shell
az vm delete -n pyclient  -g development
```

![delete_vm_1.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/delete_vm_1.png?raw=true)

Create the temporary virtual machine for troubleshooting purpose, kindly notice that if you issued vm is using Premium disk, please create the virtual machine with size **Standard_DS1_v2**

```bash
az vm create -g development --image RedHat:RHEL:7.3:latest --admin-username azureuser --admin-password Azuretroubleshooting123! --name temp20180312 --size Standard_A1
```

And the Virtual Machine is accessable via the default Account/Password azureuser/Azuretroubleshooting123!![create_temp_vm_1.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/create_temp_vm_1.png?raw=true)

Attach the issued os disk to the temporary virtual machine 

```bash
az vm disk attach --disk d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000 --resource-group development --vm-name temp20180312
```

Follow the chroot procedue to troubleshoot the issue on temporary virtual machine. After the troubleshooting fix, detach the disk from temporary virtual machine. 

```bash
az vm disk detach -g development --vm-name temp20180312 -n d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000
```

Recreate the virtual machine based on the modificed the os disk 

```bash
az vm create --name pyclient --resource-group development --location southeastasia --nics pyclient348  --size Standard_DS1 --os-type Linux --attach-os-disk d-dbf17031ca524e749b3d5d77802b9a76-osdisk-000
```

![vm_recreation_1.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/vm_recreation_1.png?raw=true)
Attach the data disk of the original virtual machine 

```shell
az vm disk attach --disk testvol --resource-group development --vm-name pyclient --caching None
```

(Optional) Enable boot diagnostics after recreation

```bash
az vm boot-diagnostics enable --name pyclient --resource-group development --storage https://developenv.blob.core.windows.net
```

### unmanaged disk

For the umanaged disk, all the commands will be generated automatically as well and you don't really need to care about the command line difference. 
The backup procedure is a little bit diferent, you need to use storage blob copy to do the backup 

```bash
az storage container create -n 2018-03-12-06-28 --account-name encrption
az storage blob copy start -u https://encrption.blob.core.windows.net/vhds/osdisk_24332149de.vhd -b osdisk_24332149de_bak.vhd -c 2018-03-12-06-28 --account-name encrption
```

### Encrypted Virtual Machine

Backup your vhd. For managed disk you need to create a snapshot for backup purpose and you could create a cloned VHD from the snapshot. For unmanaged disk, the backup procedure is a little bit diferent, you need to use storage blob copy to do the backup 

Here comes the example from managed disk. 

```bash
az snapshot create -g encryption --source testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1 --name testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1 -snapshot
//Create new disk
az disk create --resource-group encryption --source testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1-snapshot --name testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1-copy --sku Standard_LRS
```

Optional, you can allocate the public IP as static 

```bash
az network public-ip update --resource-group encryption --name testencryption-ip --allocation-method Static
```

Delete the current virtual machine with below command

```bash
az vm delete -n testencryption  -g encryption
```

![delete_vm_encry.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/delete_vm_encry.png?raw=true)

Create tempory troubleshooting virtual machine. If the virtual machine used premium disk, please create the virtual machine with size Standard_DS1_v2. The username/passowrd is azureuser/Azuretroubleshooting123!

```bash
az vm create -g encryption --image RedHat:RHEL:7.3:latest --admin-username azureuser --admin-password Azuretroubleshooting123! --name temp20180312 --size Standard_A1
```

![create_temp_vm_2.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/create_temp_vm_2.png?raw=true)
Update the encryption settings of the temporay virtual machine. To add the bek key the troubleshooting virtual machine

```bash
az vm update -n temp20180312 -g encryption --set storageProfile.osDisk.encryptionSettings.diskEncryptionKey="{'secretUrl': 'https://keyvault20180227.vault.azure.net/secrets/c6d0e079-27c5-4871-8727-77a24b97cabe/42354e4e16014c9ea8e3bdd5fdd51a2b', 'sourceVault': {'id': '/subscriptions/0f96dbcb-37cf-4c89-94ac-f9672a0ec207/resourceGroups/encryption/providers/Microsoft.KeyVault/vaults/keyvault20180227'}}" storageProfile.osDisk.encryptionSettings.keyEncryptionKey="{'keyUrl': 'https://keyvault20180227.vault.azure.net/keys/Key20180227/ca695b53ab964684b94648948f4ebc12', 'sourceVault': {'id': '/subscriptions/0f96dbcb-37cf-4c89-94ac-f9672a0ec207/resourceGroups/encryption/providers/Microsoft.KeyVault/vaults/keyvault20180227'}}" storageProfile.osDisk.encryptionSettings.Enabled=true
```

![enable_encryption_settings_on_temp_vm.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/enable_encryption_settings_on_temp_vm.png?raw=true)
Remove the encryption settings of the issued os disk 

```bash
az disk update -n testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1 -g encryption --set encryptionSettings.enabled=false encryptionSettings.diskEncryptionKey=null encryptionSettings.keyEncryptionKey=null
```

![remove_encryption_settings_os_disk.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/remove_encryption_settings_os_disk.png?raw=true)
After the settings change, we could be able to attach the issued os disk to the temporay virtual machine

```bash
az vm disk attach --disk testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1 --resource-group encryption --vm-name temp20180312
```

Then you could be able to login the temporay virtual machine and follow the procedure below to unlock the encrypted disk.  In this case the bek key is sdc1 and issued virtual machine is sdd 

```bash
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
fd0      2:0    1    4K  0 disk
sda      8:0    0   32G  0 disk
├─sda1   8:1    0  500M  0 part /boot
└─sda2   8:2    0 31.5G  0 part /
sdb      8:16   0   70G  0 disk
└─sdb1   8:17   0   70G  0 part /mnt/resource
sdc      8:32   0   48M  0 disk
└─sdc1   8:33   0   47M  0 part
sdd      8:48   0   32G  0 disk
├─sdd1   8:49   0  500M  0 part
└─sdd2   8:50   0 31.5G  0 part
```

Create rescue folder below

```bash
mkdir /{investigatekey,investigateboot,investigateroot}
```

Mount key boot folder sepeartely 

```bash
mount /dev/sdc1 /investigatekey
mount -o nouuid /dev/sdd1 /investigateboot
```

unlocked the issued os disk 

```bash
cryptsetup luksOpen --key-file /investigatekey/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader /dev/sdd2 investigateosencrypt
```

mount the root directory 

```bash
mount -o nouuid /dev/mapper/investigateosencrypt /investigateroot
```

Get everything there 

```bash
# ls /investigateroot/
bin   dev  home  lib64  mnt  proc  run   srv  temptest  tmp  var
boot  etc  lib   media  opt  root  sbin  sys  test      usr
```

After the troubleshooting, detach the issued os disk from temporary virtual machine. 

```bash
az vm disk detach -g encryption --vm-name temp20180312 -n testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1
```

Recreate the virtual machine 

```bash
az vm create --name testencryption --resource-group encryption --location southeastasia --nics testencryption172  --size Standard_D2s_v3 --os-type Linux --attach-os-disk testencryption_OsDisk_1_dee24872f6f345e5a814198023a480a1
```

![recreate_vm_3.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/recreate_vm_3.png?raw=true)

Attach all the data disk back to the recreated virtual machine 

```bash
az vm disk attach --disk encyrptiondata --resource-group encryption --vm-name testencryption --caching None
```

Since all the Encryption settings are missing after recreation, we need to set the encryption settings back to the recreated virtual machine 

```bash
az vm update -n testencryption -g encryption --set storageProfile.osDisk.encryptionSettings.diskEncryptionKey="{'secretUrl': 'https://keyvault20180227.vault.azure.net/secrets/c6d0e079-27c5-4871-8727-77a24b97cabe/42354e4e16014c9ea8e3bdd5fdd51a2b', 'sourceVault': {'id': '/subscriptions/0f96dbcb-37cf-4c89-94ac-f9672a0ec207/resourceGroups/encryption/providers/Microsoft.KeyVault/vaults/keyvault20180227'}}" storageProfile.osDisk.encryptionSettings.keyEncryptionKey="{'keyUrl': 'https://keyvault20180227.vault.azure.net/keys/Key20180227/ca695b53ab964684b94648948f4ebc12', 'sourceVault': {'id': '/subscriptions/0f96dbcb-37cf-4c89-94ac-f9672a0ec207/resourceGroups/encryption/providers/Microsoft.KeyVault/vaults/keyvault20180227'}}" storageProfile.osDisk.encryptionSettings.Enabled=true
```

The re-created virtual machine will loss all the extensions by default, we need to manually enable the encryption extension back. And we need customer to provide the service principal password and if customer cannot remember that, we could reset the credential manually
Reset the SP password

```bash
az ad sp reset-credentials --name d460d86d-6460-4601-bd1d-451031ba45dd --password yingpassword123!
```

![reset_credentials.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/reset_credentials.png?raw=true)
Enable the encryption extension again, it will deallcoate and start the vm again and it might take some time. Be patient 

```bash
az vm encryption enable --resource-group encryption --name testencryption --aad-client-id d460d86d-6460-4601-bd1d-451031ba45dd --aad-client-secret "yingpassword123!" --disk-encryption-keyvault keyvault20180227 --key-encryption-key Key20180227 --volume-type ALL
```

![enable_encryption_extension.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/enable_encryption_extension.png?raw=true)
After enable the extension, check the status 

```bash
az vm encryption show -n testencryption -g encryption
```

![encryption_status2.png](https://github.com/sundaxi/materials/blob/master/pics/az_vm_create/encryption_status2.png?raw=true)
(Optional) Enable the boot diagnostics log, it is suggested for any linux issue RCA

```bash
az vm boot-diagnostics enable --name testencryption --resource-group encryption --storage https://encrption.blob.core.windows.net/
```

### Supplement

The command ouput was saved as "operation.log" under the directory 
The virtual machine's show paremeters was saved as "GetVm.log"

## Contact

For any issue, kindly contact below 
&copy; yinsun@microsoft.com 
&copy; azlinuxsme@microsoft.com 






































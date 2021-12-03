#### How to Disable Swap

These steps were used on `ThinkCentre` machine. Your benchmark machine might require a different way to do this.

##### 1. Disable Swap
```shell script
$ free --giga
$ cat /etc/fstab
$ sudo sed -i '/ swap / s/^/#/' /etc/fstab
$ sudo swapoff -a 
$ free --giga
```

##### 2. Verify Swap is still disabled after reboot
```shell script
$ sudo reboot 
```
After reboot:
```shell script
$ free --giga
```
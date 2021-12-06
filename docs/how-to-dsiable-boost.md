#### How to Disable Boost

These steps were used on `ThinkCentre` machine. Your benchmark machine might require a different way to do this.

##### 1. Disable Boost
```shell script
$ sudo su
$ vim /sys/devices/system/cpu/cpufreq/boost
# replace 1 with 0
```

##### 2. Verify Boost is still disabled after reboot
```shell script
$ sudo reboot 
```
After reboot:
```shell script
$ cat /sys/devices/system/cpu/cpufreq/boost
0
```

Note that this might not work and you will need to do this at BIOS level:
https://techlibrary.hpe.com/docs/iss/proliant_uefi/UEFI_TM_030617/s_enable_intel_boost_tech.html

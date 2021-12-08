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

#### 3. Disable Boost on startup if Boost setting gets re-enabled after reboot and you can't disable it at BIOS level
```shell script
$ vim /etc/disable_boost.sh
# Add this to /etc/disable_boost.sh
#!/bin/bash

echo "0" | sudo tee /sys/devices/system/cpu/cpufreq/boost


$ chmod +x disable_boost.sh 
$ crontab -e
$ @reboot /etc/disable_boost.sh
```

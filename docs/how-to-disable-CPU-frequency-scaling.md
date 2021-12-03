#### How to Disable CPU Frequency Scaling

These steps were used on `ThinkCentre` machine. Your benchmark machine might require a different way to do this.

##### 1. Disable CPU Frequency Scaling
```shell script
$ sudo apt-get install cpufrequtils
$ sudo su
$ touch /etc/default/cpufrequtils
$ echo GOVERNOR="performance" > /etc/default/cpufrequtils
$ exit
$ sudo systemctl restart cpufrequtils
$ sudo systemctl disable ondemand
$ cpufreq-info
```

You should see `current policy` with `governor "performance"` for each CPU:
```shell script
...
current policy: frequency should be within 1.20 GHz and 3.60 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
...
```

##### 2. Verify CPU Frequency Scaling is still disabled after reboot
```shell script
$ reboot
```
Run this script
```shell script
$ for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  echo $i
  cat $i
done
 ```

You should see this for each CPU:
```shell script
/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu10/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu11/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu12/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu13/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu14/cpufreq/scaling_governor
performance
/sys/devices/system/cpu/cpu15/cpufreq/scaling_governor
```

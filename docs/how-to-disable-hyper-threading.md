#### How to Disable Hyper-Threading

These steps were used on `ThinkCentre` machine. Your benchmark machine might require a different way to do this.

##### 1. Check how many threads are enabled:
```shell script
$ lscpu | grep -e Socket -e Core -e Thread
Thread(s) per core:              2
Core(s) per socket:              6
Socket(s):                       1

$ lscpu --extended
CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE    MAXMHZ    MINMHZ
  0    0      0    0 0:0:0:0          yes 3300.0000 1400.0000
  1    0      0    1 1:1:1:0          yes 3300.0000 1400.0000
  2    0      0    2 2:2:2:0          yes 3300.0000 1400.0000
  3    0      0    3 3:3:3:1          yes 3300.0000 1400.0000
  4    0      0    4 4:4:4:1          yes 3300.0000 1400.0000
  5    0      0    5 5:5:5:1          yes 3300.0000 1400.0000
  6    0      0    0 0:0:0:0          yes 3300.0000 1400.0000
  7    0      0    1 1:1:1:0          yes 3300.0000 1400.0000
  8    0      0    2 2:2:2:0          yes 3300.0000 1400.0000
  9    0      0    3 3:3:3:1          yes 3300.0000 1400.0000
 10    0      0    4 4:4:4:1          yes 3300.0000 1400.0000
 11    0      0    5 5:5:5:1          yes 3300.0000 1400.0000

$ grep -H . /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | sort -n -t ':' -k 2 -u
/sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0,6
/sys/devices/system/cpu/cpu1/topology/thread_siblings_list:1,7
/sys/devices/system/cpu/cpu2/topology/thread_siblings_list:2,8
/sys/devices/system/cpu/cpu3/topology/thread_siblings_list:3,9
/sys/devices/system/cpu/cpu10/topology/thread_siblings_list:4,10
/sys/devices/system/cpu/cpu11/topology/thread_siblings_list:5,11

$ cat /sys/devices/system/cpu/smt/control
on
```

##### 2. Disable hyperthreading (add `nosmt` to `GRUB_CMDLINE_LINUX_DEFAULT`):
```shell script
$ sudo su
$ vim /etc/default/grub

GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nosmt"
```

##### 3. Generate configuration file
```shell script
$ grub-mkconfig -o /boot/grub/grub.cfg
Sourcing file `/etc/default/grub'
Sourcing file `/etc/default/grub.d/init-select.cfg'
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-5.6.0-1052-oem
Found initrd image: /boot/initrd.img-5.6.0-1052-oem
Found Windows Boot Manager on /dev/nvme0n1p1@/EFI/Microsoft/Boot/bootmgfw.efi
Adding boot menu entry for UEFI Firmware Settings
done
```

##### 4. Reboot
```shell script
$ reboot
```

##### 5. Check how many threads are enabled (you should see 1 thread per core):
```shell script
$ lscpu | grep -e Socket -e Core -e Thread
Thread(s) per core:              1
Core(s) per socket:              6
Socket(s):                       1

$ lscpu --extended
CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE    MAXMHZ    MINMHZ
  0    0      0    0 0:0:0:0          yes 3300.0000 1400.0000
  1    0      0    1 1:1:1:0          yes 3300.0000 1400.0000
  2    0      0    2 2:2:2:0          yes 3300.0000 1400.0000
  3    0      0    3 3:3:3:1          yes 3300.0000 1400.0000
  4    0      0    4 4:4:4:1          yes 3300.0000 1400.0000
  5    0      0    5 5:5:5:1          yes 3300.0000 1400.0000
  6    -      -    - :::               no         -         -
  7    -      -    - :::               no         -         -
  8    -      -    - :::               no         -         -
  9    -      -    - :::               no         -         -
 10    -      -    - :::               no         -         -
 11    -      -    - :::               no         -         -
 
$ grep -H . /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | sort -n -t ':' -k 2 -u
/sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0
/sys/devices/system/cpu/cpu1/topology/thread_siblings_list:1
/sys/devices/system/cpu/cpu2/topology/thread_siblings_list:2
/sys/devices/system/cpu/cpu3/topology/thread_siblings_list:3
/sys/devices/system/cpu/cpu4/topology/thread_siblings_list:4
/sys/devices/system/cpu/cpu5/topology/thread_siblings_list:5

$ cat /sys/devices/system/cpu/smt/control
off
```

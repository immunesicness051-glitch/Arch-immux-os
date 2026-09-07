# Append security enforcement parameters to the default kernel boot options
# Edit /etc/default/grub or systemd-boot configuration:
# lsm=landlock,lockdown,yama,apparmor,bpf

# Enable AppArmor system initialization
systemctl enable apparmor.service

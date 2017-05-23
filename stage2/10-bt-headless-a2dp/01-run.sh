#!/bin/bash -e

install -m 644 files/dnsmasq.pan0 ${ROOTFS_DIR}/etc/dnsmasq.d/
install -m 644 files/interfaces.pan0 ${ROOTFS_DIR}/etc/network/interfaces.d/
install -m 644 files/pan0-server.service ${ROOTFS_DIR}/lib/systemd/system
install -m 644 files/btauto-agent.service ${ROOTFS_DIR}/lib/systemd/system
install -m 755 files/btauto-agent.py ${ROOTFS_DIR}/usr/bin
install -m 644 files/pulseaudio.service ${ROOTFS_DIR}/lib/systemd/system


on_chroot << EOF
systemctl daemon-reload
systemctl enable dnsmasq.service
systemctl enable pan0-server.service
systemctl enable btauto-agent.service
systemctl enable pulseaudio.service
systemctl enable ssh.service

EOF


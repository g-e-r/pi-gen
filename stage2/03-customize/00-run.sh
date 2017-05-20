#!/bin/bash -e

install -m 644 files/dnsmasq.pan0 ${ROOTFS_DIR}/etc/dnsmasq.d/
install -m 644 files/interfaces.pan0 ${ROOTFS_DIR}/etc/network/interfaces.d/
install -m 644 files/hosts ${ROOTFS_DIR}/etc/hosts
install -m 644 files/pan0-server.service ${ROOTFS_DIR}/etc/systemd/system
install -m 644 files/btauto-agent.service ${ROOTFS_DIR}/etc/systemd/system
install -m 755 files/btauto-agent.py ${ROOTFS_DIR}/usr/bin

on_chroot << EOF
systemctl daemon-reload
systemctl enable dnsmasq
systemctl enable pan0-server
systemctl enable btauto-agent
systemctl enable ssh

EOF


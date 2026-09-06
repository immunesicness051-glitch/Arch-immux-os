#!/usr/bin/env python3
import sys
from bcc import BPF

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <Sandbox-Interface> <Kali-Forensic-Interface>")
    print("Example: sudo python3 immux_mirror.py anbox0 eth1")
    sys.exit(1)

sandbox_iface = sys.argv[1]
kali_iface = sys.argv[2]

# eBPF Kernel Code - Injects packet mirroring directly into host sockets
ebpf_code = """
#include <uapi/linux/bpf.h>
#include <uapi/linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

BPF_INTERFACE_MAP(mirror_port, int, int, 1);

int silent_stream_mirror(struct __sk_buff *skb) {
    // Clone target packet and route out the monitoring channel anonymously
    int key = 0;
    int *ifindex = mirror_port.lookup(&key);
    
    if (ifindex) {
        bpf_clone_redirect(skb, *ifindex, 0); // 0 flags indicates mirror to target index
    }
    
    return TC_ACT_OK; // Allow original traffic flow without malware knowing
}
"""

print(f"[*] Initializing eBPF engine hooks on {sandbox_iface}...")
try:
    # Compile and load the kernel code
    b = BPF(text=ebpf_code)
    fn = b.load_func("silent_stream_mirror", BPF.SCHED_CLS)
    
    # Retrieve system index numbers for local network devices
    import socket
    import struct
    import fcntl

    def get_ifindex(ifname):
        # Bind socket interface indexes dynamically
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifr = struct.pack('256s', ifname.encode('utf-8')[:15])
        res = fcntl.ioctl(s.fileno(), 0x8933, ifr) # SIOCGIFINDEX query code
        return struct.unpack('I', res[16:20])[0]

    kali_index = get_ifindex(kali_iface)
    
    # Map the output target dynamically into the BPF program memory array
    mirror_map = b.get_table("mirror_port")
    mirror_map[0] = kali_index

    print(f"[+] eBPF program attached. Cloned packets routing down interface index: {kali_index}")
    print("[*] Streaming diagnostic logs into Kali workspace console... Press Ctrl+C to stop.")
    
    # Keep running to sustain kernel programmatic insertion loop
    while True:
        try:
            b.trace_print()
        except KeyboardInterrupt:
            print("\\n[*] Detaching engine. Forensic observation loop concluded safely.")
            break

except Exception as e:
    print(f"[-] Execution error mapping kernel components: {e}")
    sys.exit(1)

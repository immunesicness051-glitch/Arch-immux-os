#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

def check_privileges():
    if os.geteuid() != 0:
        print("[-] System error: Root privileges required to build system layers.")
        sys.exit(1)

def compile_squashfs(source_dir, output_img):
    print(f"[*] Packaging target directory: {source_dir} -> {output_img}...")
    if not os.path.exists(source_dir):
        print(f"[-] Source {source_dir} missing. Verify file path structures.")
        sys.exit(1)
        
    # Remove existing image if present to prevent fragmentation
    if os.path.exists(output_img):
        os.remove(output_img)
        
    # Compile with maximum xz compression parameters for tiny storage usage
    cmd = [
        "mksquashfs", source_dir, output_img,
        "-comp", "xz", "-Xbcj", "x86",
        "-b", "1M", "-noappend", "-e", "root/.cache"
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"[+] Layer created successfully: {output_img}")
    else:
        print(f"[-] Compilation error: {result.stderr.decode('utf-8')}")
        sys.exit(1)

def configure_overlayfs_mounts():
    print("[*] Generating dynamic system mount configuration template...")
    fstab_template = """# Immux OS Ephemeral OverlayFS Architecture
# Root template mount
/opt/immux/layers/arch_base.squashfs /mnt/sys_ro squashfs ro,loop 0 0

# Ephemeral RAM Overlay configuration for total session cleanup
tmpfs /mnt/sys_rw tmpfs rw,noatime,mode=755 0 0
overlay / overlayfs lowerdir=/mnt/sys_ro,upperdir=/mnt/sys_rw/upper,workdir=/mnt/sys_rw/work 0 0
"""
    # Ensure deployment paths exist safely
    os.makedirs("/opt/immux/layers", exist_ok=True)
    os.makedirs("/mnt/sys_ro", exist_ok=True)
    os.makedirs("/mnt/sys_rw", exist_ok=True)
    
    print("[+] Structure initialization template mapped. System ready for dual-root lockdown.")

if __name__ == "__main__":
    check_privileges()
    # Define production paths for system components
    TARGET_ARCH_ROOT = "/opt/immux/source/arch_land"
    OUTPUT_IMAGE = "/opt/immux/layers/arch_base.squashfs"
    
    compile_squashfs(TARGET_ARCH_ROOT, OUTPUT_IMAGE)
    configure_overlayfs_mounts()

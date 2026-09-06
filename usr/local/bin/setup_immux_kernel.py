#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

# Color Codes for Output Telemetry
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[31}m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_CYAN   = "\033[36m"

def log_info(msg: str): print(f"{C_CYAN}[*]{C_RESET} {msg}")
def log_ok(msg: str): print(f"{C_GREEN}[+]{C_RESET} {msg}")
def log_warn(msg: str): print(f"{C_YELLOW}[!]{C_RESET} {msg}")
def log_err(msg: str): print(f"{C_RED}[-]{C_RESET} {msg}"); sys.exit(1)

def enforce_root():
    if os.geteuid() != 0:
        log_err("Administrative root authority required to load kernel structures.")

def discover_host_environment() -> str:
    """Identifies if the script is executing inside Arch Linux or Alpine Linux."""
    if os.path.exists("/etc/arch-release"):
        return "arch"
    elif os.path.exists("/etc/alpine-release"):
        return "alpine"
    return "unknown"

def verify_hardware_virtualization():
    log_info("Inspecting CPU flags for native KVM hardware capabilities...")
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        if "vmx" in cpuinfo or "svm" in cpuinfo:
            log_ok("Hardware virtualization extensions (Intel VT-x / AMD-V) detected.")
        else:
            log_warn("No virtualization flags identified. Verify BIOS/UEFI settings.")
    except Exception as e:
        log_err(f"Failed parsing hardware cpuinfo register: {e}")

def load_kvm_subsystems():
    log_info("Deploying native KVM kernel virtualization modules...")
    # Attempt loading the base module engine
    subprocess.run(["modprobe", "kvm"], check=True)
    
    # Identify target hardware chip sets safely to determine architecture modprobe routing
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpu_data = f.read().lower()
        if "intel" in cpu_data:
            subprocess.run(["modprobe", "kvm_intel"], check=True)
            log_ok("Intel KVM hardware abstraction modules bound to running kernel.")
        elif "amd" in cpu_data:
            subprocess.run(["modprobe", "kvm_amd"], check=True)
            log_ok("AMD KVM hardware abstraction modules bound to running kernel.")
    except Exception as e:
        log_warn(f"Module load lookahead warning: {e}")

def load_waydroid_binders():
    log_info("Injecting Waydroid IPC kernel communications framework...")
    # Build binder allocation strings mimicking custom platform inputs
    binder_cmd = ["modprobe", "binder_linux", "devices=binder,hwbinder,vndbinder"]
    result = subprocess.run(binder_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        log_ok("Android binder IPC devices initialized at location: /dev/binderfs")
    else:
        log_warn("Host kernel configuration blocks binder_linux module compilation.")
        log_warn("Ensure CONFIG_ANDROID_BINDER_IPC=m and CONFIG_ANDROID_BINDERFS=y are flag active.")

def install_layer_dependencies(host_type: str, user_account: str = "immux_user"):
    log_info(f"Targeting layer dependency installation routines for profile: {host_type.upper()}")
    
    if host_type == "arch":
        # Check package manager dependencies
        if shutil.which("pacman"):
            log_info("Synchronizing core virtualization tools down to the Arch userland workspace...")
            subprocess.run(["pacman", "-Syu", "--noconfirm", "qemu-full", "libvirt", "virt-manager"], check=True)
            subprocess.run(["systemctl", "enable", "--now", "libvirtd"], check=True)
            # Provision system group overrides to bypass sudo requirements for standard tasks
            subprocess.run(["usermod", "-aG", "kvm,libvirt", user_account], check=True)
            log_ok("Arch Linux hardware virtualization stacks activated.")
            
    elif host_type == "alpine":
        if shutil.which("apk"):
            log_info("Injecting container engine runtimes inside Alpine userland workspace...")
            subprocess.run(["apk", "update"], check=True)
            subprocess.run(["apk", "add", "qemu", "qemu-img", "libvirt", "dbus", "polkit"], check=True)
            # Route OpenRC service commands cleanly
            subprocess.run(["rc-update", "add", "libvirtd", "default"], check=True)
            subprocess.run(["addgroup", user_account, "kvm"], check=True)
            subprocess.run(["addgroup", user_account, "libvirt"], check=True)
            log_ok("Alpine Linux fallback core tools configured successfully.")

if __name__ == "__main__":
    enforce_root()
    host = discover_host_environment()
    if host == "unknown":
        log_err("Unsupported host deployment profile layer context. Aborting system creation.")
        
    print(f"\n{C_BOLD}=== IMMUX OS :: HYBRID VIRTUALIZATION ENGINE INITIALIZATION ==={C_RESET}")
    verify_hardware_virtualization()
    load_kvm_subsystems()
    load_waydroid_binders()
    
    # Target system validation checks passed. Map structural requirements down to the host layers.
    # Replace 'root' with your target profile execution username if needed
    install_layer_dependencies(host_type=host, user_account="root")
    print(f"{C_BOLD}==================================================================={C_RESET}\n")

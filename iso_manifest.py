# iso_manifest.py
ISO_POOL = {
    "4m_linux_core": {
        "title": "4M Linux 32.0 Core",
        "thumbnail": "/home/immux/assets/thumbnails/4mlinux.png",
        "local_path": "/mnt/reserved_space/iso/4m-core.iso",
        "cloud_url": "https://archive.org",
        "boot_cmd": "loopback loop (hd0,msdos2)/iso/4m-core.iso"
    },
    "custom_winboat": {
        "title": "WinBoat Hybrid Live",
        "thumbnail": "/home/immux/assets/thumbnails/winboat.png",
        "local_path": "/mnt/reserved_space/iso/winboat-latest.iso",
        "cloud_url": "https://your-cloud-bucket.co",
        "boot_cmd": "loopback loop (hd0,msdos2)/iso/winboat-latest.iso"
    }
}

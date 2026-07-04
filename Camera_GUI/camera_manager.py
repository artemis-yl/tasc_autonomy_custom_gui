import subprocess


class CameraManager:
    """
    Maps logical camera names → Windows FriendlyName → device index
    """

    def __init__(self):
        self.camera_map = {
            "Orbbec / Front": {"friendly_name": "Orbbec"},
            "WebCam / Back": {"friendly_name": "UVC HD Camera"},
            "IP Cam / Top": {"friendly_name": "USB Camera"},
            "IR Cam / ARM": {"friendly_name": "IR"},
        }

        self._cached_indices = {}

    
        self._devices = self._get_windows_camera_list()

    
    def _get_windows_camera_list(self):
        try:
            result = subprocess.check_output(
                [
                    "powershell",
                    "-Command",
                    "Get-PnpDevice -Class Camera | Select -Expand FriendlyName"
                ],
                text=True,
                stderr=subprocess.DEVNULL
            )

            return [
                line.strip()
                for line in result.splitlines()
                if line.strip()
            ]

        except Exception as e:
            print(f"[CameraManager ERROR] Failed to list cameras: {e}")
            return []

    
    def resolve_index(self, camera_name):
        if camera_name in self._cached_indices:
            return self._cached_indices[camera_name]

        if camera_name not in self.camera_map:
            print(f"[CameraManager ERROR] Unknown camera: {camera_name}")
            return None

        target_name = self.camera_map[camera_name]["friendly_name"].lower()

        devices = self._devices  

        print(f"[CameraManager] Looking for: {camera_name}")
        print(f"[CameraManager] Target Friendly Name: {target_name}")

        for i, dev in enumerate(devices):
            dev_lower = dev.lower()
            print(f"[CameraManager] [{i}] {dev}")

            if target_name in dev_lower:
                print(f"[CameraManager] MATCH FOUND → index {i}")
                self._cached_indices[camera_name] = i
                return i

        print("[CameraManager ERROR] No matching camera found")
        return None


    def dump(self):
        print("\n[CameraManager] Registered Cameras:")
        for k, v in self.camera_map.items():
            print(f" - {k}: {v['friendly_name']}")
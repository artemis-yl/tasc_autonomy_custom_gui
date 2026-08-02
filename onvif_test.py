from control_onvif import ONVIFCameraSettings

CAMERA_IP = "192.168.1.116"
ONVIF_PORT = 6688
USERNAME = "admin"
PASSWORD = ""

# Profile 0 Bitrate Range: 0-8192 
# Profile 1 Bitrate Range: 0-2048

def main():
    try:
        PROFILE_INDEX = int(input("Enter Profile Number (0 or 1): "))
        camera_settings = ONVIFCameraSettings(camera_ip=CAMERA_IP, onvif_port=ONVIF_PORT, username=USERNAME, password=PASSWORD, profile_index=PROFILE_INDEX)
        print("Current camera settings:")
        camera_settings.print_current_settings()
        exit = 1
        while exit:
            NEW_WIDTH = int(input("Enter new width: "))
            NEW_HEIGHT = int(input("Enter new height: "))
            NEW_FPS = int(input("Enter new fps: "))
            NEW_BITRATE_KBPS = int(input("Enter new bitrate: "))
            camera_settings.change_resolution(NEW_WIDTH, NEW_HEIGHT)
            camera_settings.change_fps(NEW_FPS)
            camera_settings.change_bitrate(NEW_BITRATE_KBPS)
            exit = int(input("Exit? Input 0: "))
    except Exception as error:
        print(f"Camera error: {error}")

if __name__ == "__main__":
    main()
from onvif import ONVIFCamera
from zeep.transports import Transport

class ONVIFCameraSettings:
    def __init__(self, camera_ip: str, onvif_port: int, username: str, password: str, profile_index: int = 0):
        transport = Transport(operation_timeout=1)
        try:
            self.camera = ONVIFCamera(camera_ip, onvif_port, username, password, transport=transport)
        except Exception as e:
            print(f"Connection failed: {e}")
        print(f"Connection to IP {camera_ip}:{onvif_port}")
        self.media = self.camera.create_media_service()
        self.profiles = self.media.GetProfiles()
        if profile_index < 0 or profile_index >= len(self.profiles):
            raise IndexError(f"Invalid profile index {profile_index}. " f"Camera has {len(self.profiles)} profiles.")
        self.profile = self.profiles[profile_index]

    def get_encoder_config(self):
        """Retrieve the latest video encoder configuration with GetVideoEncoderConfiguration() method."""
        configuration_token = (self.profile.VideoEncoderConfiguration.token)
        return self.media.GetVideoEncoderConfiguration({"ConfigurationToken": configuration_token})

    def save_encoder_config(self, config):
        """Save the updated video encoder configuration."""
        request = self.media.create_type("SetVideoEncoderConfiguration")
        request.Configuration = config
        request.ForcePersistence = True
        self.media.SetVideoEncoderConfiguration(request)

    def print_current_settings(self):
        """Print the current resolution, FPS, bitrate, and encoding."""
        config = self.get_encoder_config()
        print(f"Profile name: {self.profile.Name}")
        print(f"Encoding: {config.Encoding}")
        if config.Resolution:
            print(f"Resolution: " f"{config.Resolution.Width}x" f"{config.Resolution.Height}")
        if config.RateControl:
            print(f"FPS: "f"{config.RateControl.FrameRateLimit}")
            print(f"Bitrate: " f"{config.RateControl.BitrateLimit} kbps")
            print(f"Encoding interval: " f"{config.RateControl.EncodingInterval}")

    def change_resolution(self, new_width: int, new_height: int):
        """Change only the camera resolution."""
        if new_width <= 0 or new_height <= 0:
            raise ValueError("Width and height must be greater than zero.")
        config = self.get_encoder_config()
        print(f"Current resolution: " f"{config.Resolution.Width}x" f"{config.Resolution.Height}")
        config.Resolution.Width = new_width
        config.Resolution.Height = new_height
        self.save_encoder_config(config)
        updated_config = self.get_encoder_config()
        applied_width = updated_config.Resolution.Width
        applied_height = updated_config.Resolution.Height
        print(f"Requested resolution: " f"{new_width}x{new_height}")
        print(f"Applied resolution: " f"{applied_width}x{applied_height}")
        return applied_width, applied_height

    def change_fps(self, new_fps: int):
        """Change only the camera frame rate."""
        if new_fps <= 0:
            raise ValueError("FPS must be greater than zero.")
        config = self.get_encoder_config()
        if not config.RateControl:
            raise RuntimeError("RateControl is not available for this profile.")
        current_fps = config.RateControl.FrameRateLimit
        print(f"Current FPS: {current_fps}")
        config.RateControl.FrameRateLimit = new_fps
        self.save_encoder_config(config)
        updated_config = self.get_encoder_config()
        applied_fps = updated_config.RateControl.FrameRateLimit
        print(f"Requested FPS: {new_fps}")
        print(f"Applied FPS: {applied_fps}")
        return applied_fps

    def change_bitrate(self, new_bitrate_kbps: int):
        """Change only the camera bitrate limit."""
        if new_bitrate_kbps <= 0:
            raise ValueError("Bitrate must be greater than zero.")
        config = self.get_encoder_config()
        if not config.RateControl:
            raise RuntimeError("RateControl is not available for this profile.")
        current_bitrate = config.RateControl.BitrateLimit
        print(f"Current bitrate: " f"{current_bitrate} kbps")
        config.RateControl.BitrateLimit = new_bitrate_kbps
        self.save_encoder_config(config)
        updated_config = self.get_encoder_config()
        applied_bitrate = (updated_config.RateControl.BitrateLimit)
        print(f"Requested bitrate: " f"{new_bitrate_kbps} kbps")
        print(f"Applied bitrate: " f"{applied_bitrate} kbps")
        return applied_bitrate
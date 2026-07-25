JETSON_IP = "192.168.1.7"
IP_RTSP_PORT = 8554
IP_ONVIF_PORT = 6688

CAMERA_INFO = {
    "Orbbec / Front" : {
        "type" : "usb",
        "name" : "orbbec_color",   
        "place" : "front",
        "ip" : JETSON_IP,
        "port" : 7092,
    },
    "Webcam / Back" : {
        "type" : "usb",
        "name" : "back",  
        "place" : "back",
        "ip" : JETSON_IP,
        "port" : 7092,
    },           
    "IP Cam / Top" : {
        "type" : "ip",
        "name" : "top",   
        "place" : "top",
        "ip" : "192.168.1.117",
        "port" : IP_RTSP_PORT,
        "onvif_port" : IP_ONVIF_PORT
    },            
    "IP Cam 2 / ARM" : {
        "type" : "ip",
        "name" : "arm",   
        "place" : "arm",
        "ip" : "192.168.1.116", "port" : IP_RTSP_PORT, 
        "onvif_port" : IP_ONVIF_PORT
      }, 
}

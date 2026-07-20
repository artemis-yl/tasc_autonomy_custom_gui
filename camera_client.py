import json
from PySide6.QtCore import QObject, Slot
from PySide6.QtNetwork import QTcpSocket, QAbstractSocket

#Check
class CameraTcpClient(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = QTcpSocket(self)
        
        # Connect signals
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.readyRead.connect(self.on_data_received)
        self.socket.errorOccurred.connect(self.on_error_occurred)

    def connect_to_server(self, host: str = "127.0.0.1", port: int = 8080):
        if self.socket.state() == QAbstractSocket.SocketState.UnconnectedState:
            print(f"Connecting to TCP server at {host}:{port}...")
            self.socket.connectToHost(host, port)

    def send_camera_command(self, action: str, camera_type: str, resolution: str = "640x480", fps: int = 30):
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            payload = {
                "state": action.lower(),       # "play", "stop", "pause"
                "camera": camera_type.lower(), # "arm", "back", "mina"
                "resolution": resolution,
                "fps": fps
            }
            packet = (json.dumps(payload) + "\n").encode('utf-8')
            self.socket.write(packet)
        else:
            print("Cannot send command; Socket not connected.")


    def send_json(self, payload: dict) -> bool:
        """Send an arbitrary JSON-serializable dict to the server as a
        newline-terminated packet. Use this when the caller has already
        built a full settings dict (e.g. from a UI) rather than going
        through send_camera_command's fixed set of fields.
 
        Returns True if the packet was written, False if the socket
        wasn't connected (nothing is queued/retried).
        """
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            packet = (json.dumps(payload) + "\n").encode('utf-8')
            self.socket.write(packet)
            return True
        else:
            print("Cannot send command; Socket not connected.")
            return False
        
    @Slot()
    def on_connected(self):
        print("Successfully connected to the streamer TCP server!")

    @Slot()
    def on_disconnected(self):
        print("Disconnected from the streamer TCP server.")

    @Slot()
    def on_data_received(self):
        while self.socket.canReadLine():
            line = self.socket.readLine().data().decode('utf-8').strip()
            print(f"Server response: {line}")

    @Slot(QAbstractSocket.SocketError)
    def on_error_occurred(self, socket_error):
        print(f"Socket Error: {self.socket.errorString()}")

# Quick standalone test block
if __name__ == "__main__":
    from PySide6.QtCore import QCoreApplication
    import sys
    import signal  # <--- Add this import
    
    # This allows Ctrl+C to actually kill the Qt application
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QCoreApplication(sys.argv)
    client = CameraTcpClient()
    client.connect_to_server("127.0.0.1", 8080)
    
    # Send a quick test packet right when it connects successfully
    client.socket.connected.connect(lambda: client.send_camera_command("play", "back"))
    
    sys.exit(app.exec())
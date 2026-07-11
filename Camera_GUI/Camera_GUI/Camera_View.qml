import QtQuick

Rectangle {
    id: root
    property string cameraName: "Camera"

    color: "#1a1a1a"
    border.width: 2
    border.color: "#444444"

    Text {
        anchors.centerIn: parent
        text: root.cameraName + "\n[No Signal]"
        color: "#555555"
        font.pointSize: 16
        horizontalAlignment: Text.AlignHCenter
    }
}
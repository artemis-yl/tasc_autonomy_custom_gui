import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts

Window {
    width: 1920
    height: 1080
    visible: true
    title: qsTr("Sample?")

    //width: Constants.width
    //height: Constants.height

    //color: Constants.backgroundColor

    Rectangle {
        id: frontCamera
        x: 0
        y: 0
        width: 1280
        height: 720
        color: "#ffffff"
        border.width: 2
    }

    Rectangle {
        id: backCamera
        x: 0
        y: 720
        width: 640
        height: 360
        color: "#ffffff"
        border.width: 2
    }

    Rectangle {
        id: topCamera
        x: 640
        y: 720
        width: 640
        height: 360
        color: "#ffffff"
        border.width: 2
    }

    Rectangle {
        id: armCamera
        x: 1280
        y: 720
        width: 640
        height: 360
        color: "#ffffff"
        border.width: 2
    }

    Rectangle {
        id: buttonPanel
        x: 1280
        y: 0
        width: 640
        height: 720
        color: "#ffffff"
        border.width: 2

        Button {
            id: frontCameraPlayButton
            width: 200
            text: qsTr("Orbbec /Front")
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: 10
            anchors.topMargin: 10
            Layout.preferredHeight: 40
            Layout.preferredWidth: 180
            font.pointSize: 16
        }

        RowLayout {
            id: rowLayout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: frontCameraPlayButton.bottom
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            anchors.topMargin: 10
            layoutDirection: Qt.LeftToRight
            uniformCellSizes: true
            Button {
                id: armCameraPlayButton
                width: 200
                text: qsTr("IR Cam / ARM ")
                font.pointSize: 16
                Layout.preferredWidth: 180
                Layout.preferredHeight: 40
                onClicked: playClicked()
            }

            Button {
                id: backCameraPlayButton
                width: 200
                text: qsTr("WebCam / Back")
                font.pointSize: 16
                Layout.preferredWidth: 180
                Layout.preferredHeight: 40
            }

            Button {
                id: topCameraPlayButton
                width: 200
                text: qsTr("IP Cam / Top")
                font.pointSize: 16
                Layout.preferredWidth: 180
                Layout.preferredHeight: 40
            }
        }
    }
}
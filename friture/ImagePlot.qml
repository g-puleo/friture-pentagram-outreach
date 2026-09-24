import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import QtQuick.Controls 2.15
import Friture 1.0

Item {
    id: container
    anchors.fill: parent

    Plot {
        id: plot
        scopedata: viewModel

        Repeater {
            model: plot.scopedata.plot_items

            SpectrogramItem {
                anchors.fill: parent
                curve: modelData
            }
        }

        PentagramOverlay {
            anchors.fill: parent
            visible: viewModel.pentagram_enabled
            lines: viewModel.staff_lines
        }
    }

    ToolButton {
        id: pentagramButton
        z: 1
        anchors.top: parent.top
        anchors.right: parent.right
        // not checkable: the checked state always follows the view model
        checked: viewModel.pentagram_enabled
        onClicked: viewModel.setPentagramEnabled(!viewModel.pentagram_enabled)
        text: "\u{1D11E}"
        font.family: "Noto Music"
        font.pixelSize: 20
        ToolTip.visible: hovered
        ToolTip.text: "Pentagram: show the piano grand staff over the spectrogram"
    }
}

import QtQuick 2.15
import QtQuick.Shapes 1.15

// Grand staff drawn over the spectrogram. Each line sits at the true
// equal-temperament frequency of its note (A4 = 440 Hz), so the background
// is left transparent and the spectrogram shows through.
Item {
    id: overlay

    // list of {y, kind, name, freq}, y relative from the bottom (0) to the top (1)
    property var lines: []

    readonly property color lineColor: Qt.rgba(1, 1, 1, 0.85)
    readonly property color shadowColor: Qt.rgba(0, 0, 0, 0.6)
    readonly property color middleCColor: "#ffc14d"
    readonly property string musicFont: "Noto Music"
    readonly property real leftMargin: 6

    function lineY(name) {
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].name === name) {
                return (1. - lines[i].y) * overlay.height
            }
        }
        return NaN
    }

    readonly property real trebleTop: lineY("F5")
    readonly property real trebleBottom: lineY("E4")
    readonly property real bassTop: lineY("A3")
    readonly property real bassBottom: lineY("G2")
    readonly property bool trebleVisible: !isNaN(trebleTop) && !isNaN(trebleBottom)
    readonly property bool bassVisible: !isNaN(bassTop) && !isNaN(bassBottom)

    // smallest pixel distance between two neighbouring lines
    readonly property real minLineSpacing: {
        var spacing = Infinity
        for (var i = 1; i < lines.length; i++) {
            spacing = Math.min(spacing, (lines[i].y - lines[i - 1].y) * overlay.height)
        }
        return spacing
    }
    // note labels are hidden when the plot is too short for them to be readable
    readonly property bool labelsVisible: minLineSpacing >= 16

    Repeater {
        model: overlay.lines

        Item {
            id: staffLine
            required property var modelData
            readonly property bool isMiddleC: modelData.kind === "middle_c"

            x: 0
            width: overlay.width
            y: Math.round((1. - modelData.y) * overlay.height)
            height: 1

            // dark shadow so that the line reads on any colormap
            Rectangle {
                visible: !staffLine.isMiddleC
                x: 0; y: 0
                width: parent.width; height: 3
                color: overlay.shadowColor
            }
            Rectangle {
                visible: !staffLine.isMiddleC
                x: 0; y: 0
                width: parent.width; height: 2
                color: overlay.lineColor
            }

            Shape {
                visible: staffLine.isMiddleC
                anchors.fill: parent
                ShapePath {
                    strokeWidth: 3
                    strokeColor: overlay.shadowColor
                    fillColor: "transparent"
                    strokeStyle: ShapePath.DashLine
                    dashPattern: [4, 3]
                    startX: 0; startY: 1.5
                    PathLine { x: staffLine.width; y: 1.5 }
                }
                ShapePath {
                    strokeWidth: 2
                    strokeColor: overlay.middleCColor
                    fillColor: "transparent"
                    strokeStyle: ShapePath.DashLine
                    dashPattern: [4, 3]
                    startX: 0; startY: 1
                    PathLine { x: staffLine.width; y: 1 }
                }
            }

            Text {
                visible: overlay.labelsVisible
                anchors.right: parent.right
                anchors.rightMargin: 4
                anchors.bottom: parent.top
                text: staffLine.modelData.name + "  " + staffLine.modelData.freq.toFixed(1) + " Hz"
                font.pixelSize: 10
                color: staffLine.isMiddleC ? overlay.middleCColor : overlay.lineColor
                style: Text.Outline
                styleColor: overlay.shadowColor
            }
        }
    }

    // vertical bar joining the two staves, as on a piano score
    Rectangle {
        visible: overlay.trebleVisible && overlay.bassVisible
        x: overlay.leftMargin
        y: overlay.trebleTop
        width: 2
        height: overlay.bassBottom - overlay.trebleTop + 2
        color: overlay.lineColor
    }

    TextMetrics {
        id: trebleMetrics
        font.family: overlay.musicFont
        font.pixelSize: 100
        text: "\u{1D11E}"
    }

    TextMetrics {
        id: bassMetrics
        font.family: overlay.musicFont
        font.pixelSize: 100
        text: "\u{1D122}"
    }

    // treble (violin) clef, a.k.a. G clef: its curl wraps around the G4 line
    Text {
        id: trebleClef
        visible: overlay.trebleVisible
        readonly property real staffHeight: overlay.trebleBottom - overlay.trebleTop
        // the glyph rises above the top line and its tail hangs below the bottom line
        readonly property real glyphTop: overlay.trebleTop - 0.35 * staffHeight
        readonly property real glyphHeight: 1.75 * staffHeight
        readonly property real k: trebleMetrics.tightBoundingRect.height > 0 ? glyphHeight / trebleMetrics.tightBoundingRect.height : 1

        text: trebleMetrics.text
        font.family: overlay.musicFont
        font.pixelSize: Math.max(1, 100 * k)
        color: overlay.lineColor
        style: Text.Outline
        styleColor: overlay.shadowColor
        x: overlay.leftMargin + 6 - trebleMetrics.tightBoundingRect.x * k
        y: glyphTop - trebleMetrics.tightBoundingRect.y * k - baselineOffset
    }

    // bass clef, a.k.a. F clef: its two dots straddle the F3 line
    Text {
        id: bassClef
        visible: overlay.bassVisible
        readonly property real staffHeight: overlay.bassBottom - overlay.bassTop
        readonly property real glyphTop: overlay.bassTop
        readonly property real glyphHeight: 0.8 * staffHeight
        readonly property real k: bassMetrics.tightBoundingRect.height > 0 ? glyphHeight / bassMetrics.tightBoundingRect.height : 1

        text: bassMetrics.text
        font.family: overlay.musicFont
        font.pixelSize: Math.max(1, 100 * k)
        color: overlay.lineColor
        style: Text.Outline
        styleColor: overlay.shadowColor
        x: overlay.leftMargin + 6 - bassMetrics.tightBoundingRect.x * k
        y: glyphTop - bassMetrics.tightBoundingRect.y * k - baselineOffset
    }
}

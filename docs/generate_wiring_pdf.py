from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "conexiones_esp32_tinaco.pdf"


def line(c, x1, y1, x2, y2, color=colors.black, width=2, dash=None):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    if dash:
        c.setDash(dash)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def label(c, text, x, y, size=9, color=colors.black, bold=False):
    c.saveState()
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, text)
    c.restoreState()


def rect(c, x, y, w, h, fill, stroke=colors.black, radius=8):
    c.saveState()
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.restoreState()


def pin(c, x, y, text, side="right"):
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#1f2933"))
    c.rect(x - 4, y - 4, 8, 8, stroke=1, fill=1)
    c.setFont("Helvetica", 7)
    if side == "right":
        c.drawString(x + 8, y - 3, text)
    else:
        c.drawRightString(x - 8, y - 3, text)
    c.restoreState()


def draw_button(c, x, y, text):
    rect(c, x, y, 92, 38, colors.HexColor("#ffffff"), colors.HexColor("#64748b"), radius=6)
    c.circle(x + 18, y + 19, 5, stroke=1, fill=0)
    c.circle(x + 74, y + 19, 5, stroke=1, fill=0)
    line(c, x + 24, y + 19, x + 66, y + 27, colors.HexColor("#475569"), 2)
    label(c, text, x + 8, y - 13, 8, colors.HexColor("#111827"), bold=True)


def polyline(c, points, color=colors.black, width=2, dash=None):
    for start, end in zip(points, points[1:]):
        line(c, start[0], start[1], end[0], end[1], color, width, dash)


def draw_diagram(c):
    c.setTitle("Conexiones ESP32 Tinaco")
    width, height = landscape(A4)

    label(c, "Diagrama de conexiones - ESP32 controlador de bomba", 38, height - 34, 16, bold=True)
    label(c, "El ESP32 controla el modulo relevador. La bomba va por COM y NO.", 38, height - 52, 9, colors.HexColor("#475569"))

    # Low voltage area.
    rect(c, 28, 88, 500, 438, colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1"), radius=10)
    label(c, "CONTROL / BAJO VOLTAJE", 42, 506, 10, colors.HexColor("#334155"), bold=True)

    # High voltage area.
    rect(c, 545, 88, 268, 438, colors.HexColor("#fff7ed"), colors.HexColor("#fdba74"), radius=10)
    label(c, "POTENCIA BOMBA 110/220 VAC", 562, 506, 10, colors.HexColor("#9a3412"), bold=True)
    line(c, 536, 88, 536, 526, colors.HexColor("#94a3b8"), 1, dash=[5, 5])
    label(c, "Separacion entre control y potencia", 445, 532, 8, colors.HexColor("#64748b"))

    # ESP32 board.
    esp_x, esp_y, esp_w, esp_h = 66, 230, 170, 244
    rect(c, esp_x, esp_y, esp_w, esp_h, colors.HexColor("#1d9bb2"), colors.HexColor("#0f4c5c"), radius=14)
    rect(c, esp_x + 42, esp_y + 182, 88, 38, colors.HexColor("#d9e2ec"), colors.HexColor("#52616b"), radius=6)
    label(c, "ESP32", esp_x + 64, esp_y + 202, 13, colors.HexColor("#0b3142"), bold=True)
    label(c, "DevKit", esp_x + 63, esp_y + 187, 10, colors.HexColor("#0b3142"))
    rect(c, esp_x + 55, esp_y + 18, 60, 36, colors.HexColor("#0f172a"), colors.HexColor("#020617"), radius=4)
    label(c, "USB", esp_x + 74, esp_y + 33, 9, colors.white, bold=True)

    esp_left_x = esp_x
    esp_right_x = esp_x + esp_w
    esp_pins = {
        "gpio32": (esp_left_x, 380),
        "gpio33": (esp_left_x, 350),
        "gpio25": (esp_left_x, 320),
        "gpio27": (esp_left_x, 290),
        "gnd_buttons": (esp_left_x, 260),
        "vin": (esp_right_x, 398),
        "gnd_relay": (esp_right_x, 368),
        "gpio26": (esp_right_x, 338),
    }
    for name, text in [
        ("gpio32", "GPIO32"),
        ("gpio33", "GPIO33"),
        ("gpio25", "GPIO25"),
        ("gpio27", "GPIO27"),
        ("gnd_buttons", "GND"),
    ]:
        pin(c, *esp_pins[name], text, "left")
    for name, text in [("vin", "VIN/5V"), ("gnd_relay", "GND"), ("gpio26", "GPIO26")]:
        pin(c, *esp_pins[name], text, "right")

    # Relay module.
    relay_x, relay_y, relay_w, relay_h = 342, 282, 148, 166
    rect(c, relay_x, relay_y, relay_w, relay_h, colors.HexColor("#2563eb"), colors.HexColor("#1e3a8a"), radius=10)
    label(c, "MODULO", relay_x + 46, relay_y + 142, 10, colors.white, bold=True)
    label(c, "RELEVADOR", relay_x + 34, relay_y + 128, 10, colors.white, bold=True)
    rect(c, relay_x + 42, relay_y + 52, 68, 46, colors.HexColor("#dbeafe"), colors.HexColor("#1e40af"), radius=5)
    label(c, "RELAY", relay_x + 57, relay_y + 70, 11, colors.HexColor("#1e3a8a"), bold=True)

    relay_pins = {
        "dc+": (relay_x, 408),
        "dc-": (relay_x, 378),
        "in": (relay_x, 348),
        "com": (relay_x + relay_w, 408),
        "no": (relay_x + relay_w, 378),
        "nc": (relay_x + relay_w, 348),
    }
    for name, text in [("dc+", "DC+/VCC"), ("dc-", "DC-/GND"), ("in", "IN")]:
        pin(c, *relay_pins[name], text, "left")
    for name, text in [("com", "COM"), ("no", "NO"), ("nc", "NC")]:
        pin(c, *relay_pins[name], text, "right")

    # Buttons and low-voltage wiring.
    label(c, "Botones fisicos: un lado al GPIO y el otro lado a GND", 56, 198, 9, colors.HexColor("#334155"), bold=True)
    buttons = [
        ("1/4", 56, 138, "gpio32", colors.HexColor("#0ea5e9")),
        ("1/2", 166, 138, "gpio33", colors.HexColor("#0ea5e9")),
        ("Vacio", 276, 138, "gpio25", colors.HexColor("#0ea5e9")),
        ("Stop", 386, 138, "gpio27", colors.HexColor("#dc2626")),
    ]
    ground_bus_y = 112
    line(c, 48, ground_bus_y, 504, ground_bus_y, colors.HexColor("#64748b"), 2)
    label(c, "Barra comun GND de botones", 58, 98, 8, colors.HexColor("#475569"))
    polyline(c, [esp_pins["gnd_buttons"], (48, 260), (48, ground_bus_y)], colors.HexColor("#64748b"), 2)

    for text, bx, by, esp_key, color in buttons:
        draw_button(c, bx, by, "Boton " + text)
        button_signal = (bx + 18, by + 38)
        button_gnd = (bx + 74, by)
        esp_pin = esp_pins[esp_key]
        polyline(c, [esp_pin, (esp_pin[0] - 18, esp_pin[1]), (esp_pin[0] - 18, button_signal[1] + 12), (button_signal[0], button_signal[1] + 12), button_signal], color, 2)
        polyline(c, [button_gnd, (button_gnd[0], ground_bus_y)], colors.HexColor("#64748b"), 2)

    # Control wires to relay module.
    polyline(c, [esp_pins["vin"], (286, 398), relay_pins["dc+"]], colors.HexColor("#ef4444"), 2)
    polyline(c, [esp_pins["gnd_relay"], (286, 368), relay_pins["dc-"]], colors.HexColor("#64748b"), 2)
    polyline(c, [esp_pins["gpio26"], (296, 338), (296, 348), relay_pins["in"]], colors.HexColor("#16a34a"), 2)
    label(c, "GPIO26 -> IN", 270, 326, 8, colors.HexColor("#166534"), bold=True)
    label(c, "5V", 290, 403, 8, colors.HexColor("#991b1b"), bold=True)
    label(c, "GND", 290, 373, 8, colors.HexColor("#475569"), bold=True)

    # AC source and pump.
    source_x, source_y = 590, 128
    pump_x, pump_y = 622, 362
    rect(c, source_x, source_y, 160, 92, colors.white, colors.HexColor("#9a3412"), radius=8)
    label(c, "ALIMENTACION", source_x + 38, source_y + 64, 10, colors.HexColor("#7c2d12"), bold=True)
    label(c, "110/220 VAC", source_x + 47, source_y + 47, 10, colors.HexColor("#7c2d12"))
    label(c, "L / Fase", source_x + 16, source_y + 25, 8)
    label(c, "N / Neutro", source_x + 16, source_y + 11, 8)
    label(c, "Tierra", source_x + 102, source_y + 11, 8)

    rect(c, pump_x, pump_y, 150, 76, colors.HexColor("#e0f2fe"), colors.HexColor("#0369a1"), radius=10)
    c.circle(pump_x + 55, pump_y + 38, 22, stroke=1, fill=0)
    label(c, "BOMBA", pump_x + 36, pump_y + 36, 11, colors.HexColor("#075985"), bold=True)
    label(c, "agua", pump_x + 43, pump_y + 21, 8, colors.HexColor("#075985"))
    label(c, "L", pump_x - 12, pump_y + 53, 8, colors.HexColor("#991b1b"), bold=True)
    label(c, "N", pump_x + 158, pump_y + 37, 8, colors.HexColor("#1d4ed8"), bold=True)
    label(c, "T", pump_x + 158, pump_y + 21, 8, colors.HexColor("#15803d"), bold=True)

    # High-voltage wiring.
    source_l = (source_x + 30, source_y + 27)
    source_n = (source_x + 30, source_y + 13)
    source_t = (source_x + 126, source_y + 13)
    pump_l = (pump_x, pump_y + 56)
    pump_n = (pump_x + 150, pump_y + 40)
    pump_t = (pump_x + 150, pump_y + 24)
    polyline(c, [source_l, (560, source_l[1]), (560, 408), relay_pins["com"]], colors.HexColor("#dc2626"), 2.2)
    polyline(c, [relay_pins["no"], (560, 378), (560, pump_l[1]), pump_l], colors.HexColor("#dc2626"), 2.2)
    polyline(c, [source_n, (786, source_n[1]), (786, pump_n[1]), pump_n], colors.HexColor("#2563eb"), 2.2)
    polyline(c, [source_t, (802, source_t[1]), (802, pump_t[1]), pump_t], colors.HexColor("#16a34a"), 2.2)
    label(c, "Fase -> COM", 568, 412, 8, colors.HexColor("#991b1b"), bold=True)
    label(c, "NO -> L bomba", 568, 382, 8, colors.HexColor("#991b1b"), bold=True)
    label(c, "Neutro directo", 646, 286, 8, colors.HexColor("#1d4ed8"), bold=True)
    label(c, "Tierra directa", 684, 258, 8, colors.HexColor("#15803d"), bold=True)

    # Warning box.
    rect(c, 562, 94, 226, 28, colors.HexColor("#fff1f2"), colors.HexColor("#fb7185"), radius=7)
    label(c, "La bomba NO va al ESP32.", 576, 110, 9, colors.HexColor("#9f1239"), bold=True)
    label(c, "Usa caja y protecciones electricas.", 576, 99, 7, colors.HexColor("#9f1239"))

    c.showPage()


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = [
        ["Funcion", "Pin ESP32", "Conexion"],
        ["Relevador IN", "GPIO 26", "Entrada IN del modulo relevador"],
        ["Boton 1/4", "GPIO 32", "Boton entre GPIO32 y GND"],
        ["Boton 1/2", "GPIO 33", "Boton entre GPIO33 y GND"],
        ["Boton Vacio", "GPIO 25", "Boton entre GPIO25 y GND"],
        ["Boton Detener", "GPIO 27", "Boton entre GPIO27 y GND"],
        ["GND comun", "GND", "GND del relevador y botones"],
        ["Alimentacion relevador", "VIN/5V", "VCC del modulo, si tu modulo es de 5V"],
    ]

    c = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4))
    width, height = landscape(A4)
    label(c, "Guia rapida de conexiones - ESP32 controlador de bomba", 42, height - 48, 17, bold=True)
    label(c, "Tabla de pines del firmware", 42, height - 80, 12, colors.HexColor("#334155"), bold=True)

    y = height - 112
    col_x = [42, 190, 300]
    row_h = 24
    c.setFillColor(colors.HexColor("#0f766e"))
    c.rect(42, y - 5, 700, row_h, stroke=0, fill=1)
    label(c, "Funcion", col_x[0] + 8, y + 2, 9, colors.white, bold=True)
    label(c, "Pin ESP32", col_x[1] + 8, y + 2, 9, colors.white, bold=True)
    label(c, "Conexion", col_x[2] + 8, y + 2, 9, colors.white, bold=True)
    y -= row_h
    for row in data[1:]:
        c.setFillColor(colors.white if int((height - y) / row_h) % 2 == 0 else colors.HexColor("#f8fafc"))
        c.rect(42, y - 5, 700, row_h, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.rect(42, y - 5, 700, row_h, stroke=1, fill=0)
        label(c, row[0], col_x[0] + 8, y + 2, 8)
        label(c, row[1], col_x[1] + 8, y + 2, 8)
        label(c, row[2], col_x[2] + 8, y + 2, 8)
        y -= row_h

    rect(c, 42, 128, 700, 74, colors.HexColor("#fff7ed"), colors.HexColor("#fdba74"), radius=8)
    label(c, "Notas importantes", 58, 178, 11, colors.HexColor("#9a3412"), bold=True)
    label(c, "El ESP32 solo controla el modulo relevador; no alimenta la bomba.", 58, 160, 9)
    label(c, "Para 110/220V usa caja cerrada, fusible/breaker, tierra fisica y cableado adecuado.", 58, 144, 9)
    label(c, "Si el relevador activa al reves, cambia RELAY_ACTIVE_LOW en src/main.cpp.", 58, 128, 9)
    c.showPage()

    draw_diagram(c)
    c.save()


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)

#include <Arduino.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>

// Cambia estos pines segun tu placa/cableado.
constexpr uint8_t RELAY_PIN = 26;
constexpr uint8_t BUTTON_QUARTER_PIN = 32;
constexpr uint8_t BUTTON_HALF_PIN = 33;
constexpr uint8_t BUTTON_EMPTY_PIN = 25;
constexpr uint8_t BUTTON_STOP_PIN = 27;
constexpr uint8_t STATUS_LED_PIN = 2;

// Muchos modulos de relevador azules son activos en LOW.
constexpr bool RELAY_ACTIVE_LOW = true;

constexpr const char *AP_SSID = "Tinaco-Doser";
constexpr const char *AP_PASSWORD = "12345678";

constexpr unsigned long DEBOUNCE_MS = 60;
constexpr unsigned long DEFAULT_QUARTER_SECONDS = 5 * 60;
constexpr unsigned long DEFAULT_HALF_SECONDS = 10 * 60;
constexpr unsigned long DEFAULT_EMPTY_SECONDS = 20 * 60;

enum class FillMode {
  Idle,
  Quarter,
  Half,
  Empty,
};

struct Config {
  unsigned long quarterSeconds;
  unsigned long halfSeconds;
  unsigned long emptySeconds;
};

struct Button {
  uint8_t pin;
  bool stablePressed;
  bool lastReadingPressed;
  unsigned long lastChangeMs;
};

Preferences preferences;
WebServer server(80);

Config config{};
FillMode currentMode = FillMode::Idle;
unsigned long runStartedMs = 0;
unsigned long runDurationMs = 0;

Button buttonQuarter{BUTTON_QUARTER_PIN, false, false, 0};
Button buttonHalf{BUTTON_HALF_PIN, false, false, 0};
Button buttonEmpty{BUTTON_EMPTY_PIN, false, false, 0};
Button buttonStop{BUTTON_STOP_PIN, false, false, 0};

void setRelay(bool enabled) {
  const uint8_t level = RELAY_ACTIVE_LOW
                            ? (enabled ? LOW : HIGH)
                            : (enabled ? HIGH : LOW);
  digitalWrite(RELAY_PIN, level);
  digitalWrite(STATUS_LED_PIN, enabled ? HIGH : LOW);
}

const char *modeName(FillMode mode) {
  switch (mode) {
  case FillMode::Quarter:
    return "1/4";
  case FillMode::Half:
    return "1/2";
  case FillMode::Empty:
    return "Vacio";
  case FillMode::Idle:
  default:
    return "Detenido";
  }
}

unsigned long durationForMode(FillMode mode) {
  switch (mode) {
  case FillMode::Quarter:
    return config.quarterSeconds;
  case FillMode::Half:
    return config.halfSeconds;
  case FillMode::Empty:
    return config.emptySeconds;
  case FillMode::Idle:
  default:
    return 0;
  }
}

void stopPump() {
  currentMode = FillMode::Idle;
  runDurationMs = 0;
  runStartedMs = 0;
  setRelay(false);
  Serial.println("Bomba detenida");
}

void startPump(FillMode mode) {
  const unsigned long seconds = durationForMode(mode);
  if (seconds == 0) {
    stopPump();
    return;
  }

  currentMode = mode;
  runStartedMs = millis();
  runDurationMs = seconds * 1000UL;
  setRelay(true);

  Serial.printf("Bomba encendida: %s por %lu segundos\n", modeName(mode),
                seconds);
}

unsigned long remainingSeconds() {
  if (currentMode == FillMode::Idle) {
    return 0;
  }

  const unsigned long elapsed = millis() - runStartedMs;
  if (elapsed >= runDurationMs) {
    return 0;
  }

  return (runDurationMs - elapsed + 999UL) / 1000UL;
}

bool pressedEvent(Button &button) {
  const bool readingPressed = digitalRead(button.pin) == LOW;
  const unsigned long now = millis();

  if (readingPressed != button.lastReadingPressed) {
    button.lastReadingPressed = readingPressed;
    button.lastChangeMs = now;
  }

  if ((now - button.lastChangeMs) < DEBOUNCE_MS) {
    return false;
  }

  if (readingPressed != button.stablePressed) {
    button.stablePressed = readingPressed;
    return button.stablePressed;
  }

  return false;
}

String htmlPage() {
  String page;
  page.reserve(3600);
  page += F("<!doctype html><html lang='es'><head><meta charset='utf-8'>");
  page += F("<meta name='viewport' content='width=device-width,initial-scale=1'>");
  page += F("<title>Control Tinaco</title><style>");
  page += F("body{font-family:Arial,sans-serif;margin:0;background:#f7f7f3;color:#222}");
  page += F("main{max-width:680px;margin:auto;padding:24px}");
  page += F("h1{font-size:28px;margin:0 0 16px}");
  page += F(".panel{background:#fff;border:1px solid #ddd;border-radius:8px;padding:18px;margin:14px 0}");
  page += F("label{display:block;margin:14px 0 6px;font-weight:700}");
  page += F("input{box-sizing:border-box;width:100%;font-size:18px;padding:10px;border:1px solid #bbb;border-radius:6px}");
  page += F("button,a.btn{display:inline-block;margin:8px 8px 0 0;padding:11px 14px;border-radius:6px;border:0;background:#146c43;color:#fff;text-decoration:none;font-size:16px}");
  page += F("button.stop,a.stop{background:#b42318}.muted{color:#666}.status{font-size:18px}");
  page += F("</style></head><body><main><h1>Control Tinaco</h1>");
  page += F("<section class='panel status'><strong>Estado:</strong> ");
  page += modeName(currentMode);
  page += F("<br><strong>Restante:</strong> ");
  page += String(remainingSeconds());
  page += F(" segundos</section>");
  page += F("<section class='panel'><h2>Arranque manual</h2>");
  page += F("<a class='btn' href='/start?mode=quarter'>1/4</a>");
  page += F("<a class='btn' href='/start?mode=half'>1/2</a>");
  page += F("<a class='btn' href='/start?mode=empty'>Vacio</a>");
  page += F("<a class='btn stop' href='/stop'>Detener</a></section>");
  page += F("<section class='panel'><h2>Tiempos</h2>");
  page += F("<form method='post' action='/save'>");
  page += F("<label>1/4 de tinaco, minutos</label><input name='quarter' type='number' min='1' max='240' value='");
  page += String(config.quarterSeconds / 60);
  page += F("'><label>1/2 tinaco, minutos</label><input name='half' type='number' min='1' max='240' value='");
  page += String(config.halfSeconds / 60);
  page += F("'><label>Tinaco vacio, minutos</label><input name='empty' type='number' min='1' max='240' value='");
  page += String(config.emptySeconds / 60);
  page += F("'><button type='submit'>Guardar</button></form>");
  page += F("<p class='muted'>Conectate al WiFi Tinaco-Doser y abre http://192.168.4.1</p>");
  page += F("</section></main></body></html>");
  return page;
}

void redirectHome() {
  server.sendHeader("Location", "/", true);
  server.send(303, "text/plain", "");
}

unsigned long minutesArgToSeconds(const String &name, unsigned long fallback) {
  if (!server.hasArg(name)) {
    return fallback;
  }

  const long minutes = server.arg(name).toInt();
  if (minutes < 1 || minutes > 240) {
    return fallback;
  }

  return static_cast<unsigned long>(minutes) * 60UL;
}

void saveConfig() {
  config.quarterSeconds = minutesArgToSeconds("quarter", config.quarterSeconds);
  config.halfSeconds = minutesArgToSeconds("half", config.halfSeconds);
  config.emptySeconds = minutesArgToSeconds("empty", config.emptySeconds);

  preferences.putULong("quarter", config.quarterSeconds);
  preferences.putULong("half", config.halfSeconds);
  preferences.putULong("empty", config.emptySeconds);

  Serial.println("Configuracion guardada");
  redirectHome();
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() { server.send(200, "text/html", htmlPage()); });

  server.on("/save", HTTP_POST, saveConfig);

  server.on("/stop", HTTP_GET, []() {
    stopPump();
    redirectHome();
  });

  server.on("/start", HTTP_GET, []() {
    const String mode = server.arg("mode");
    if (mode == "quarter") {
      startPump(FillMode::Quarter);
    } else if (mode == "half") {
      startPump(FillMode::Half);
    } else if (mode == "empty") {
      startPump(FillMode::Empty);
    }
    redirectHome();
  });

  server.onNotFound([]() { server.send(404, "text/plain", "No encontrado"); });
  server.begin();
}

void loadConfig() {
  preferences.begin("tinaco", false);
  config.quarterSeconds =
      preferences.getULong("quarter", DEFAULT_QUARTER_SECONDS);
  config.halfSeconds = preferences.getULong("half", DEFAULT_HALF_SECONDS);
  config.emptySeconds = preferences.getULong("empty", DEFAULT_EMPTY_SECONDS);
}

void setupButtons() {
  pinMode(BUTTON_QUARTER_PIN, INPUT_PULLUP);
  pinMode(BUTTON_HALF_PIN, INPUT_PULLUP);
  pinMode(BUTTON_EMPTY_PIN, INPUT_PULLUP);
  pinMode(BUTTON_STOP_PIN, INPUT_PULLUP);
}

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  setRelay(false);
  setupButtons();
  loadConfig();

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  setupWebServer();

  Serial.println();
  Serial.println("Control de tinaco listo");
  Serial.printf("WiFi: %s / clave: %s\n", AP_SSID, AP_PASSWORD);
  Serial.println("Panel: http://192.168.4.1");
}

void loop() {
  server.handleClient();

  if (pressedEvent(buttonQuarter)) {
    startPump(FillMode::Quarter);
  }
  if (pressedEvent(buttonHalf)) {
    startPump(FillMode::Half);
  }
  if (pressedEvent(buttonEmpty)) {
    startPump(FillMode::Empty);
  }
  if (pressedEvent(buttonStop)) {
    stopPump();
  }

  if (currentMode != FillMode::Idle && remainingSeconds() == 0) {
    stopPump();
  }
}

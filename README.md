# ESP32 Water Doser / Control de bomba para tinaco

Firmware para ESP32 que activa un modulo relevador durante un tiempo configurable
para llenar un tinaco desde tres estados iniciales:

- `1/4`: tiempo corto.
- `1/2`: tiempo medio.
- `Vacio`: tiempo largo.

El ESP32 crea una red WiFi propia para configurar los tiempos desde el celular.

## Funcionamiento

1. Enciende el ESP32.
2. Conectate a la red WiFi `Tinaco-Doser`.
3. Usa la clave `12345678`.
4. Abre `http://192.168.4.1`.
5. Configura los minutos para `1/4`, `1/2` y `Vacio`.
6. Arranca la bomba desde la pagina o desde botones fisicos.

Los tiempos quedan guardados en la memoria del ESP32.

## Pines por defecto

| Funcion | Pin ESP32 |
| --- | --- |
| Relevador | GPIO 26 |
| Boton 1/4 | GPIO 32 |
| Boton 1/2 | GPIO 33 |
| Boton Vacio | GPIO 25 |
| Boton Detener | GPIO 27 |
| LED estado | GPIO 2 |

Los botones van entre el pin indicado y `GND`. El firmware usa `INPUT_PULLUP`.

## Relevador

Muchos modulos de relevador azules funcionan con entrada activa en `LOW`.
Por eso el firmware trae:

```cpp
constexpr bool RELAY_ACTIVE_LOW = true;
```

Si tu modulo trabaja activo en `HIGH`, cambia ese valor a `false`.

## Seguridad electrica

El ESP32 no debe alimentar la bomba directamente. El ESP32 solo controla la
entrada del modulo relevador.

Para la bomba usa un modulo relevador/contactor con capacidad suficiente para
el voltaje y corriente reales de la bomba. La parte de corriente alterna debe
quedar en caja cerrada, con fusible/breaker, tierra fisica y cableado adecuado.
Si la bomba usa 110V/220V, pide apoyo a alguien calificado para esa conexion.

Conexion tipica de control:

- `ESP32 5V/VIN` a `VCC` del modulo relevador si el modulo es de 5V.
- `ESP32 GND` a `GND` del modulo relevador.
- `GPIO 26` a `IN` del modulo relevador.

Conexion tipica de potencia:

- Fase de alimentacion al comun `COM` del relevador.
- Normalmente abierto `NO` hacia la fase de la bomba.
- Neutro directo a la bomba.
- Tierra fisica directa a la bomba.

## Compilar y subir

Este repo esta preparado para PlatformIO:

```bash
pio run
pio run --target upload
pio device monitor
```

Tambien puedes copiar `src/main.cpp` a un sketch de Arduino IDE para ESP32.

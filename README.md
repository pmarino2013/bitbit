# BitBit

BitBit es una mascota virtual interactiva para la terminal, presentada como un daemon de desarrollo. Cuida sus métricas, evita que entre en *Kernel Panic* y resuelve minijuegos de lógica y conversión binaria.

> BitBit es una simulación: no inicia procesos en segundo plano ni modifica el estado real de tu sistema.

## Requisitos

- Python 3
- Una terminal compatible con entrada interactiva en modo cbreak (Linux y macOS)
- La biblioteca [Rich](https://github.com/Textualize/rich)

## Instalación y ejecución

Clona el repositorio y entra en su directorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd bitbit
```

Instala la dependencia y ejecuta el programa:

```bash
python3 -m pip install rich
python3 bitbit.py
```

## Cómo jugar

BitBit muestra sus métricas de CPU, RAM y entropía, su estado actual, y un registro de eventos. Usa estas teclas para interactuar:

| Tecla | Acción |
| --- | --- |
| `1` | Dar café: aumenta la CPU y un poco la entropía. |
| `2` | Ejecutar recolección de basura: libera RAM a cambio de algo de CPU. |
| `3` | Simular un `git push`: puede mejorar las métricas o provocar un error en producción. Si BitBit está en llamas, lo apaga. |
| `4` | Iniciar un desafío de puertas lógicas o de binario a decimal. |
| `R` | Reiniciar BitBit después de un *Kernel Panic*. |
| `Q` | Salir. |

Durante un desafío, introduce el resultado con una tecla (`0`–`9`) o pulsa `X` para cancelarlo. Resolverlo reduce la entropía; una respuesta incorrecta la aumenta.

¡Mantén a BitBit con vida y evita que la RAM llegue al 100 % o que la CPU caiga a 0 %!

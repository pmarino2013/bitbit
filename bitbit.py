import time
import random
import sys
import select
from collections import deque
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn
from rich.console import Console
from rich.align import Align

SPRITES = {
    "happy": [
        "   ▄▄▄▄▄▄▄   ",
        "  █ ◕   ◕ █  ",
        "  █   ‿   █  ",
        "   ▀▀▀▀▀▀▀   ",
        "    ╨   ╨    ",
    ],
    "happy_alt": [
        "   ▄▄▄▄▄▄▄   ",
        "  █ ^   ^ █  ",
        "  █   ▽   █  ",
        "   ▀▀▀▀▀▀▀   ",
        "   ╨     ╨   ",
    ],
    "lagging": [
        "   ▄▄▄▄▄▄▄   ",
        "  █ ◔   ◔ █  ",
        "  █  ~~~  █  ",
        "   ▀▀▀▀▀▀▀   ",
        "    ╨   ╨    ",
    ],
    "fire": [
        "  🔥  🔥  🔥 ",
        "   ▄▄▄▄▄▄▄   ",
        "  █ >   < █  ",
        "  █   Д   █  ",
        "   ▀▀▀▀▀▀▀   ",
    ],
    "dead": [
        "   ▄▄▄▄▄▄▄   ",
        "  █ X   X █  ",
        "  █  ───  █  ",
        "   ▀▀▀▀▀▀▀   ",
        "  [SEGFAULT] ",
    ],
    "thinking": [
        "   ▄▄▄▄▄▄▄   ",
        "  █ ◔   ◔ █  ",
        "  █   o   █  ",
        "   ▀▀▀▀▀▀▀   ",
        "    ╨   ╨    ",
    ],
}


class BitBit:
    def __init__(self):
        self.cpu = 85.0
        self.ram = 25.0
        self.entropy = 15.0
        self.uptime = 0
        self.alive = True
        self.on_fire = False
        self.frame = 0
        self.logs = deque(maxlen=6)

        # Estado del minijuego
        self.puzzle_active = False
        self.puzzle_prompt = ""
        self.puzzle_answer = ""
        self.puzzle_hint = ""

        self.log("[OK] BitBit daemon iniciado (PID 1337).")
        self.log("[INFO] Esperando comandos del operador...")

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def tick(self):
        if not self.alive:
            return

        self.uptime += 1
        self.frame = (self.frame + 1) % 2

        # El decaimiento es más lento mientras resuelves un puzzle
        factor = 0.4 if self.puzzle_active else 1.0
        self.cpu = max(0.0, self.cpu - 0.8 * factor)
        self.ram = min(100.0, self.ram + 1.1 * factor)
        self.entropy = min(100.0, self.entropy + 0.9 * factor)

        if self.on_fire:
            self.cpu = max(0.0, self.cpu - 3.5)
            self.log("[ALERT] ¡Build roto! BitBit se está quemando.")

        if self.cpu <= 0 or self.ram >= 100:
            self.alive = False
            self.puzzle_active = False
            self.log("[FATAL] KERNEL PANIC. BitBit ha muerto.")

    def get_state(self) -> str:
        if not self.alive:
            return "dead"
        if self.on_fire:
            return "fire"
        if self.puzzle_active:
            return "thinking"
        if self.ram > 75 or self.cpu < 25 or self.entropy > 80:
            return "lagging"
        return "happy" if self.frame == 0 else "happy_alt"

    # --- ACCIONES ---
    def feed_coffee(self):
        if not self.alive or self.puzzle_active:
            return
        self.cpu = min(100.0, self.cpu + 25)
        self.entropy = min(100.0, self.entropy + 5)
        self.log("$ bitbit feed --coffee -> +25% CPU.")

    def garbage_collect(self):
        if not self.alive or self.puzzle_active:
            return
        self.ram = max(0.0, self.ram - 35)
        self.cpu = max(5.0, self.cpu - 5)
        self.log("$ sudo gc -> RAM liberada (-35%).")

    def git_push(self):
        if not self.alive or self.puzzle_active:
            return
        if self.on_fire:
            self.on_fire = False
            self.log("$ git revert HEAD -> ¡Fuego extinguido!")
            return

        if random.random() < 0.75:
            self.cpu = min(100.0, self.cpu + 15)
            self.entropy = max(0.0, self.entropy - 20)
            self.log("$ git push origin main -> Build OK! (+Stats)")
        else:
            self.on_fire = True
            self.log("$ git push -f -> ¡ERROR EN PRODUCCIÓN!")

    # --- MINIJUEGO DE PUERTAS LÓGICAS / BINARIO ---
    def start_puzzle(self):
        if not self.alive or self.puzzle_active:
            return

        self.puzzle_active = True
        mode = random.choice(["logic", "binary"])

        if mode == "logic":
            a = random.randint(0, 1)
            b = random.randint(0, 1)
            gate = random.choice(["AND", "OR", "XOR", "NAND"])

            if gate == "AND":
                ans = a & b
            elif gate == "OR":
                ans = a | b
            elif gate == "XOR":
                ans = a ^ b
            else:  # NAND
                ans = int(not (a & b))

            self.puzzle_prompt = f"PUERTA LÓGICA:\n\n   [ {a} ] ──▶ {gate} ◀── [ {b} ]   =  ?"
            self.puzzle_answer = str(ans)
            self.puzzle_hint = "Presiona [0] o [1] (o [X] para cancelar)"
            self.log(f"$ bitbit debug --gate {gate} -> Esperando bit...")

        else:
            # Número del 0 al 9 para responder con una sola tecla
            num = random.randint(0, 9)
            bin_str = f"{num:04b}"
            self.puzzle_prompt = f"BINARIO A DECIMAL:\n\n   0b {bin_str}   =  ?"
            self.puzzle_answer = str(num)
            self.puzzle_hint = "Presiona una tecla del [0] al [9] (o [X] para cancelar)"
            self.log(f"$ bitbit debug --bin 0b{bin_str} -> Esperando dígito...")

    def answer_puzzle(self, key: str):
        if not self.puzzle_active:
            return

        if key == "x":
            self.puzzle_active = False
            self.log("$ debug cancelado por el usuario.")
            return

        if key == self.puzzle_answer:
            self.entropy = max(0.0, self.entropy - 35)
            self.cpu = min(100.0, self.cpu + 5)
            self.ram = min(100.0, self.ram + 3)
            self.log(f"[OK] Respuesta '{key}' correcta! Entropía -35%.")
        else:
            self.entropy = min(100.0, self.entropy + 10)
            self.log(f"[ERR] Fallaste ('{key}' != '{self.puzzle_answer}'). Entropía +10%.")

        self.puzzle_active = False

    def reboot(self):
        self.__init__()
        self.log("[SYS] Sistema reiniciado tras Kernel Panic.")


def build_ui(pet: BitBit) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="logs", size=9),
        Layout(name="footer", size=3),
    )

    status_color = "green" if pet.alive else "red"
    header_text = Text(
        f" BITBIT DAEMON v1.1 | UPTIME: {pet.uptime}s | STATUS: {'ONLINE' if pet.alive else 'PANIC'} ",
        style=f"bold {status_color}",
    )
    layout["header"].update(Panel(Align.center(header_text), border_style=status_color))

    layout["main"].split_row(
        Layout(name="sprite", ratio=1), Layout(name="right_panel", ratio=2)
    )

    # Panel Izquierdo: Sprite
    state = pet.get_state()
    sprite_lines = "\n".join(SPRITES[state])
    sprite_color = (
        "red"
        if state in ("fire", "dead")
        else ("magenta" if state == "thinking" else ("yellow" if state == "lagging" else "bright_green"))
    )
    layout["sprite"].update(
        Panel(
            Align.center(Text(sprite_lines, style=f"bold {sprite_color}"), vertical="middle"),
            title="[ Entity ]",
            border_style=sprite_color,
        )
    )

    # Panel Derecho: Métricas o Minijuego activo
    if pet.puzzle_active:
        puzzle_text = Text()
        puzzle_text.append(pet.puzzle_prompt + "\n\n", style="bold bright_magenta")
        puzzle_text.append(pet.puzzle_hint, style="dim white")
        layout["right_panel"].update(
            Panel(
                Align.center(puzzle_text, vertical="middle"),
                title="[ DEBUG CHALLENGE ]",
                border_style="bright_magenta",
            )
        )
    else:
        progress = Progress(
            TextColumn("[bold]{task.description:<12}"),
            BarColumn(bar_width=25),
            TextColumn("{task.percentage:>3.0f}%"),
        )
        progress.add_task("CPU (Energía)", completed=pet.cpu, total=100)
        progress.add_task("RAM (Basura)", completed=pet.ram, total=100)
        progress.add_task("Entropía", completed=pet.entropy, total=100)

        layout["right_panel"].update(
            Panel(Align.center(progress, vertical="middle"), title="[ htop Metrics ]", border_style="cyan")
        )

    # Logs
    log_text = Text("\n".join(pet.logs), style="dim white")
    layout["logs"].update(Panel(log_text, title="[ /var/log/bitbit.log ]", border_style="blue"))

    # Footer dinámico según contexto
    if pet.puzzle_active:
        controls = (
            "[bold magenta]MODO DEBUG ACTIVO:[/]  "
            "Ingresa el resultado numérico [bold cyan][0-9][/]   "
            "[bold yellow][X][/] Cancelar"
        )
    else:
        controls = (
            "[bold cyan][1][/] Café (CPU)   "
            "[bold cyan][2][/] sudo gc (RAM)   "
            "[bold cyan][3][/] git push   "
            "[bold magenta][4][/] Debug Puzzle   "
            "[bold yellow][R][/] Reboot   "
            "[bold red][Q][/] Salir"
        )
    layout["footer"].update(Panel(Align.center(Text.from_markup(controls)), border_style="white"))

    return layout


def main():
    import tty
    import termios

    console = Console()
    pet = BitBit()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        last_tick = time.time()

        with Live(build_ui(pet), console=console, auto_refresh=False, screen=True) as live:
            live.refresh()
            while True:
                needs_redraw = False

                rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                if rlist:
                    key = sys.stdin.read(1).lower()

                    if pet.puzzle_active:
                        # En modo puzzle, capturamos dígitos o X para salir
                        if key in "0123456789x":
                            pet.answer_puzzle(key)
                            needs_redraw = True
                    else:
                        if key == "1":
                            pet.feed_coffee()
                            needs_redraw = True
                        elif key == "2":
                            pet.garbage_collect()
                            needs_redraw = True
                        elif key == "3":
                            pet.git_push()
                            needs_redraw = True
                        elif key == "4":
                            pet.start_puzzle()
                            needs_redraw = True
                        elif key == "r":
                            pet.reboot()
                            needs_redraw = True
                        elif key == "q":
                            break

                now = time.time()
                if now - last_tick >= 1.0:
                    pet.tick()
                    last_tick = now
                    needs_redraw = True

                if needs_redraw:
                    live.update(build_ui(pet), refresh=True)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()
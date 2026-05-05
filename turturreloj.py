import tkinter as tk
import math
import time
import random
from datetime import datetime


class RelojPsicodelico:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Psicodélico - Simulación de Sistemas")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.running = True
        self.show_trails = True
        self.show_particles = True
        self.speed = 1.0
        self.phase = 0
        self.mouse_x = 500
        self.mouse_y = 350
        self.particles = []

        self.colors = [
            "#ff006e", "#fb5607", "#ffbe0b",
            "#8338ec", "#3a86ff", "#00f5d4",
            "#b5179e", "#7209b7", "#4cc9f0"
        ]

        for _ in range(120):
            self.particles.append({
                "angle": random.uniform(0, math.tau),
                "radius": random.uniform(20, 320),
                "speed": random.uniform(0.002, 0.015),
                "size": random.uniform(2, 6),
                "color": random.choice(self.colors)
            })

        self.root.bind("<Motion>", self.update_mouse)
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("t", self.toggle_trails)
        self.root.bind("p", self.toggle_particles)
        self.root.bind("+", self.increase_speed)
        self.root.bind("-", self.decrease_speed)
        self.root.bind("r", self.reset_effects)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.animate()

    def update_mouse(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def toggle_pause(self, event=None):
        self.running = not self.running

    def toggle_trails(self, event=None):
        self.show_trails = not self.show_trails

    def toggle_particles(self, event=None):
        self.show_particles = not self.show_particles

    def increase_speed(self, event=None):
        self.speed = min(self.speed + 0.2, 4)

    def decrease_speed(self, event=None):
        self.speed = max(self.speed - 0.2, 0.2)

    def reset_effects(self, event=None):
        self.speed = 1.0
        self.show_trails = True
        self.show_particles = True
        self.phase = 0

    def color_wave(self, offset=0):
        r = int(127 + 128 * math.sin(self.phase + offset))
        g = int(127 + 128 * math.sin(self.phase + offset + 2))
        b = int(127 + 128 * math.sin(self.phase + offset + 4))
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_background_spiral(self, cx, cy, w, h):
        max_radius = min(w, h) * 0.65

        for i in range(90):
            angle = self.phase * 0.6 + i * 0.28
            radius = i / 90 * max_radius

            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius

            size = 12 + 8 * math.sin(self.phase + i * 0.3)
            color = self.color_wave(i * 0.15)

            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                outline=color,
                width=2
            )

    def draw_particles(self, cx, cy):
        if not self.show_particles:
            return

        for p in self.particles:
            p["angle"] += p["speed"] * self.speed

            wobble = 25 * math.sin(self.phase * 2 + p["radius"] * 0.05)
            r = p["radius"] + wobble

            x = cx + math.cos(p["angle"]) * r
            y = cy + math.sin(p["angle"]) * r

            size = p["size"] + 2 * math.sin(self.phase * 3 + p["angle"])

            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=p["color"],
                outline=""
            )

    def draw_clock_face(self, cx, cy, radius):
        for i in range(60):
            angle = math.tau * i / 60 - math.pi / 2

            if i % 5 == 0:
                length = 28
                width = 5
                color = self.color_wave(i * 0.2)
            else:
                length = 14
                width = 2
                color = "#444444"

            outer_x = cx + math.cos(angle) * radius
            outer_y = cy + math.sin(angle) * radius

            inner_x = cx + math.cos(angle) * (radius - length)
            inner_y = cy + math.sin(angle) * (radius - length)

            self.canvas.create_line(
                inner_x, inner_y,
                outer_x, outer_y,
                fill=color,
                width=width,
                capstyle=tk.ROUND
            )

        for i in range(1, 13):
            angle = math.tau * i / 12 - math.pi / 2
            x = cx + math.cos(angle) * (radius - 60)
            y = cy + math.sin(angle) * (radius - 60)

            color = self.color_wave(i * 0.6)

            self.canvas.create_text(
                x, y,
                text=str(i),
                fill=color,
                font=("Helvetica", 22, "bold")
            )

    def draw_hand(self, cx, cy, angle, length, width, color, glow=True):
        x = cx + math.cos(angle) * length
        y = cy + math.sin(angle) * length

        if glow:
            for glow_width in range(width + 14, width, -4):
                self.canvas.create_line(
                    cx, cy, x, y,
                    fill=color,
                    width=glow_width,
                    capstyle=tk.ROUND,
                    stipple="gray25"
                )

        self.canvas.create_line(
            cx, cy, x, y,
            fill=color,
            width=width,
            capstyle=tk.ROUND
        )

        self.canvas.create_oval(
            x - width * 1.4, y - width * 1.4,
            x + width * 1.4, y + width * 1.4,
            fill=color,
            outline=""
        )

    def draw_clock(self, cx, cy, radius):
        now = datetime.now()

        hour = now.hour % 12
        minute = now.minute
        second = now.second
        micro = now.microsecond

        smooth_second = second + micro / 1_000_000
        smooth_minute = minute + smooth_second / 60
        smooth_hour = hour + smooth_minute / 60

        second_angle = math.tau * smooth_second / 60 - math.pi / 2
        minute_angle = math.tau * smooth_minute / 60 - math.pi / 2
        hour_angle = math.tau * smooth_hour / 12 - math.pi / 2

        self.draw_clock_face(cx, cy, radius)

        self.draw_hand(cx, cy, hour_angle, radius * 0.46, 12, self.color_wave(0.3))
        self.draw_hand(cx, cy, minute_angle, radius * 0.68, 8, self.color_wave(1.7))
        self.draw_hand(cx, cy, second_angle, radius * 0.82, 4, self.color_wave(3.2))

        pulse = 15 + 7 * math.sin(self.phase * 4)

        self.canvas.create_oval(
            cx - pulse, cy - pulse,
            cx + pulse, cy + pulse,
            fill=self.color_wave(5),
            outline="white",
            width=2
        )

        time_text = now.strftime("%H:%M:%S")
        date_text = now.strftime("%A, %d %B %Y")

        self.canvas.create_text(
            cx, cy + radius + 55,
            text=time_text,
            fill=self.color_wave(2),
            font=("Helvetica", 44, "bold")
        )

        self.canvas.create_text(
            cx, cy + radius + 100,
            text=date_text,
            fill="#dddddd",
            font=("Helvetica", 18)
        )

    def draw_mouse_vortex(self, cx, cy):
        distance = math.hypot(self.mouse_x - cx, self.mouse_y - cy)
        intensity = max(0.3, min(1.5, distance / 300))

        for i in range(35):
            angle = self.phase * intensity + i * 0.5
            radius = i * 5

            x = self.mouse_x + math.cos(angle) * radius
            y = self.mouse_y + math.sin(angle) * radius

            size = 4 + 3 * math.sin(self.phase + i)
            color = self.color_wave(i * 0.4)

            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                outline=color,
                width=2
            )

    def draw_help(self, w, h):
        help_text = (
            "Controles: ESPACIO pausar | T estelas | P partículas | + velocidad | - velocidad | R reset | ESC salir"
        )

        self.canvas.create_text(
            w // 2,
            h - 25,
            text=help_text,
            fill="#aaaaaa",
            font=("Helvetica", 13)
        )

        status = "RUNNING" if self.running else "PAUSADO"
        self.canvas.create_text(
            90,
            30,
            text=f"{status}  |  velocidad x{self.speed:.1f}",
            fill=self.color_wave(1),
            font=("Helvetica", 14, "bold")
        )

    def animate(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        cx = w // 2
        cy = h // 2 - 40
        radius = min(w, h) * 0.31

        if not self.show_trails:
            self.canvas.delete("all")
        else:
            self.canvas.create_rectangle(
                0, 0, w, h,
                fill="black",
                outline="",
                stipple="gray50"
            )

        if self.running:
            self.phase += 0.025 * self.speed

        self.draw_background_spiral(cx, cy, w, h)
        self.draw_particles(cx, cy)
        self.draw_mouse_vortex(cx, cy)
        self.draw_clock(cx, cy, radius)
        self.draw_help(w, h)

        self.root.after(16, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = RelojPsicodelico(root)
    root.mainloop()
import tkinter as tk
import math
import random
from datetime import datetime


class RelojPsicodelicoNormalBoxMuller:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Psicodélico con Normal + Box-Muller")
        self.root.geometry("1160x790")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Estado general
        self.running = True
        self.show_trails = True
        self.show_particles = True
        self.show_distribution = True
        self.show_box_muller = True
        self.speed = 1.0
        self.phase = 0

        # Mouse
        self.mouse_x = 580
        self.mouse_y = 395

        # Parámetros de la distribución normal
        self.mu = 0.0
        self.sigma = 1.0
        self.target_mu = random.uniform(-1.8, 1.8)
        self.target_sigma = random.uniform(0.45, 1.8)
        self.last_distribution_change = datetime.now()

        # Valores Box-Muller para las esquinas
        self.box_muller_values = []
        self.last_box_update = datetime.now()
        self.generate_box_muller_values()

        # Partículas
        self.particles = []
        self.colors = [
            "#ff006e", "#fb5607", "#ffbe0b",
            "#8338ec", "#3a86ff", "#00f5d4",
            "#b5179e", "#7209b7", "#4cc9f0",
            "#80ffdb", "#f72585"
        ]

        for _ in range(140):
            self.particles.append({
                "angle": random.uniform(0, math.tau),
                "radius": random.uniform(20, 365),
                "speed": random.uniform(0.002, 0.018),
                "size": random.uniform(2, 6),
                "color": random.choice(self.colors)
            })

        # Controles
        self.root.bind("<Motion>", self.update_mouse)
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("t", self.toggle_trails)
        self.root.bind("p", self.toggle_particles)
        self.root.bind("d", self.toggle_distribution)
        self.root.bind("b", self.toggle_box_muller)
        self.root.bind("+", self.increase_speed)
        self.root.bind("-", self.decrease_speed)
        self.root.bind("r", self.reset_effects)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.animate()

    # -------------------------
    # Controles
    # -------------------------
    def update_mouse(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def toggle_pause(self, event=None):
        self.running = not self.running

    def toggle_trails(self, event=None):
        self.show_trails = not self.show_trails

    def toggle_particles(self, event=None):
        self.show_particles = not self.show_particles

    def toggle_distribution(self, event=None):
        self.show_distribution = not self.show_distribution

    def toggle_box_muller(self, event=None):
        self.show_box_muller = not self.show_box_muller

    def increase_speed(self, event=None):
        self.speed = min(self.speed + 0.2, 4.0)

    def decrease_speed(self, event=None):
        self.speed = max(self.speed - 0.2, 0.2)

    def reset_effects(self, event=None):
        self.speed = 1.0
        self.show_trails = True
        self.show_particles = True
        self.show_distribution = True
        self.show_box_muller = True
        self.phase = 0
        self.mu = 0
        self.sigma = 1
        self.target_mu = random.uniform(-1.8, 1.8)
        self.target_sigma = random.uniform(0.45, 1.8)
        self.generate_box_muller_values()

    # -------------------------
    # Color psicodélico
    # -------------------------
    def color_wave(self, offset=0):
        r = int(127 + 128 * math.sin(self.phase + offset))
        g = int(127 + 128 * math.sin(self.phase + offset + 2))
        b = int(127 + 128 * math.sin(self.phase + offset + 4))
        return f"#{r:02x}{g:02x}{b:02x}"

    # -------------------------
    # Normal y Box-Muller
    # -------------------------
    def normal_pdf(self, x, mu, sigma):
        return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(
            -0.5 * ((x - mu) / sigma) ** 2
        )

    def normal_cdf_approx(self, x, mu, sigma):
        return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))

    def generate_box_muller_values(self):
        """
        Box-Muller:
        U1, U2 ~ Uniforme(0,1)

        R = sqrt(-2 ln(U1))
        θ = 2πU2

        Z0 = R cos(θ)
        Z1 = R sin(θ)

        Luego se transforma:
        X0 = μ + σZ0
        X1 = μ + σZ1
        """

        self.box_muller_values = []

        for _ in range(4):
            u1 = max(random.random(), 1e-12)
            u2 = random.random()

            r = math.sqrt(-2 * math.log(u1))
            theta = 2 * math.pi * u2

            z0 = r * math.cos(theta)
            z1 = r * math.sin(theta)

            x0 = self.mu + self.sigma * z0
            x1 = self.mu + self.sigma * z1

            self.box_muller_values.append({
                "u1": u1,
                "u2": u2,
                "r": r,
                "theta": theta,
                "z0": z0,
                "z1": z1,
                "x0": x0,
                "x1": x1
            })

    def update_distribution_parameters(self):
        now = datetime.now()
        elapsed = (now - self.last_distribution_change).total_seconds()

        # Cada 3 segundos cambia hacia una nueva media y sigma
        if elapsed > 3.0:
            self.target_mu = random.uniform(-2.0, 2.0)
            self.target_sigma = random.uniform(0.45, 1.9)
            self.last_distribution_change = now

        # Movimiento suave hacia los nuevos valores
        self.mu += (self.target_mu - self.mu) * 0.015 * self.speed
        self.sigma += (self.target_sigma - self.sigma) * 0.015 * self.speed

        # Cada rato se actualizan los valores Box-Muller de las esquinas
        box_elapsed = (now - self.last_box_update).total_seconds()

        if box_elapsed > 1.2:
            self.generate_box_muller_values()
            self.last_box_update = now

        # Aunque U1 y U2 cambien por saltos, X se mantiene ligado al μ y σ actuales
        for bm in self.box_muller_values:
            bm["x0"] = self.mu + self.sigma * bm["z0"]
            bm["x1"] = self.mu + self.sigma * bm["z1"]

    def draw_normal_distribution_background(self, w, h):
        if not self.show_distribution:
            return

        self.update_distribution_parameters()

        center_y = h * 0.62
        graph_height = h * 0.33
        x_min = -4
        x_max = 4

        points = []
        glow_points = []

        max_pdf = self.normal_pdf(self.mu, self.mu, self.sigma)

        for px in range(0, w + 1, 8):
            x = x_min + (px / w) * (x_max - x_min)
            y_pdf = self.normal_pdf(x, self.mu, self.sigma)

            normalized = y_pdf / max_pdf
            wave = 0.06 * math.sin(self.phase * 2 + x * 5)

            py = center_y - (normalized + wave) * graph_height

            points.append((px, py))

            glow_y = py + 8 * math.sin(self.phase + px * 0.01)
            glow_points.append((px, glow_y))

        # Líneas horizontales decorativas
        for i in range(7):
            y = center_y - i * graph_height / 6
            color = self.color_wave(i * 0.5)

            self.canvas.create_line(
                0, y, w, y,
                fill=color,
                width=1,
                stipple="gray25"
            )

        # Eje base
        self.canvas.create_line(
            0, center_y, w, center_y,
            fill="#555555",
            width=2
        )

        # Área bajo la curva
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            color = self.color_wave(i * 0.09)

            self.canvas.create_polygon(
                x1, center_y,
                x1, y1,
                x2, y2,
                x2, center_y,
                fill=color,
                outline="",
                stipple="gray50"
            )

        # Curva con glow
        for width_line in [12, 8, 5]:
            flat = []

            for x, y in glow_points:
                flat.extend([x, y])

            self.canvas.create_line(
                flat,
                fill=self.color_wave(width_line * 0.3),
                width=width_line,
                smooth=True,
                capstyle=tk.ROUND,
                stipple="gray25"
            )

        flat_points = []

        for x, y in points:
            flat_points.extend([x, y])

        self.canvas.create_line(
            flat_points,
            fill="white",
            width=3,
            smooth=True,
            capstyle=tk.ROUND
        )

        # Línea de la media
        mu_px = int((self.mu - x_min) / (x_max - x_min) * w)

        self.canvas.create_line(
            mu_px, center_y,
            mu_px, center_y - graph_height * 1.18,
            fill=self.color_wave(4),
            width=4,
            dash=(8, 8)
        )

        self.canvas.create_text(
            mu_px,
            center_y - graph_height * 1.25,
            text="μ",
            fill=self.color_wave(4),
            font=("Helvetica", 28, "bold")
        )

        # Marcas de sigma
        for k in range(-3, 4):
            x_val = self.mu + k * self.sigma

            if x_min <= x_val <= x_max:
                px = int((x_val - x_min) / (x_max - x_min) * w)

                self.canvas.create_line(
                    px, center_y - 10,
                    px, center_y + 10,
                    fill="#dddddd",
                    width=2
                )

                label = f"{k}σ" if k != 0 else "μ"

                self.canvas.create_text(
                    px,
                    center_y + 28,
                    text=label,
                    fill="#dddddd",
                    font=("Helvetica", 11, "bold")
                )

    def draw_distribution_stats(self, w, h):
        if not self.show_distribution:
            return

        variance = self.sigma ** 2
        density_at_mu = self.normal_pdf(self.mu, self.mu, self.sigma)

        p_between_1_sigma = (
            self.normal_cdf_approx(self.mu + self.sigma, self.mu, self.sigma)
            - self.normal_cdf_approx(self.mu - self.sigma, self.mu, self.sigma)
        )

        p_between_2_sigma = (
            self.normal_cdf_approx(self.mu + 2 * self.sigma, self.mu, self.sigma)
            - self.normal_cdf_approx(self.mu - 2 * self.sigma, self.mu, self.sigma)
        )

        random_x = self.mu + math.sin(self.phase * 1.7) * 2.5 * self.sigma
        density_random_x = self.normal_pdf(random_x, self.mu, self.sigma)

        stats = [
            "Normal viva de fondo",
            f"μ media ≈ {self.mu: .3f}",
            f"σ desviación ≈ {self.sigma: .3f}",
            f"σ² varianza ≈ {variance: .3f}",
            f"f(μ) densidad máx ≈ {density_at_mu: .3f}",
            f"P(μ-σ ≤ X ≤ μ+σ) ≈ {p_between_1_sigma * 100: .2f}%",
            f"P(μ-2σ ≤ X ≤ μ+2σ) ≈ {p_between_2_sigma * 100: .2f}%",
            f"x animado ≈ {random_x: .3f}",
            f"f(x animado) ≈ {density_random_x: .3f}",
        ]

        panel_x = 25
        panel_y = 105
        panel_w = 345
        panel_h = 250

        self.canvas.create_rectangle(
            panel_x,
            panel_y,
            panel_x + panel_w,
            panel_y + panel_h,
            fill="black",
            outline=self.color_wave(2),
            width=3,
            stipple="gray75"
        )

        for i, line in enumerate(stats):
            font_size = 15 if i == 0 else 13
            font_weight = "bold" if i == 0 else "normal"
            color = self.color_wave(i * 0.45) if i == 0 else "#eeeeee"

            self.canvas.create_text(
                panel_x + 18,
                panel_y + 25 + i * 25,
                text=line,
                anchor="w",
                fill=color,
                font=("Helvetica", font_size, font_weight)
            )

    def draw_box_muller_panels(self, w, h):
        if not self.show_box_muller:
            return

        panel_w = 285
        panel_h = 205
        margin = 16

        positions = [
            (margin, margin, "Box-Muller A"),
            (w - panel_w - margin, margin, "Box-Muller B"),
            (margin, h - panel_h - 55, "Box-Muller C"),
            (w - panel_w - margin, h - panel_h - 55, "Box-Muller D"),
        ]

        for i, (x, y, title) in enumerate(positions):
            bm = self.box_muller_values[i]

            # Fondo del panel
            self.canvas.create_rectangle(
                x,
                y,
                x + panel_w,
                y + panel_h,
                fill="black",
                outline=self.color_wave(i * 1.1),
                width=3,
                stipple="gray75"
            )

            # Título
            self.canvas.create_text(
                x + 14,
                y + 20,
                text=title,
                anchor="w",
                fill=self.color_wave(i * 0.9),
                font=("Helvetica", 14, "bold")
            )

            # Fórmula corta
            self.canvas.create_text(
                x + 14,
                y + 43,
                text="Z0 = √(-2 ln U1) · cos(2πU2)",
                anchor="w",
                fill="#dddddd",
                font=("Helvetica", 10)
            )

            self.canvas.create_text(
                x + 14,
                y + 60,
                text="Z1 = √(-2 ln U1) · sin(2πU2)",
                anchor="w",
                fill="#dddddd",
                font=("Helvetica", 10)
            )

            lines = [
                f"U1 = {bm['u1']:.4f}",
                f"U2 = {bm['u2']:.4f}",
                f"R = √(-2 ln U1) = {bm['r']:.4f}",
                f"θ = 2πU2 = {bm['theta']:.4f}",
                f"Z0 = R cos(θ) = {bm['z0']:.4f}",
                f"Z1 = R sin(θ) = {bm['z1']:.4f}",
                f"X0 = μ + σZ0 = {bm['x0']:.4f}",
                f"X1 = μ + σZ1 = {bm['x1']:.4f}",
            ]

            for j, line in enumerate(lines):
                self.canvas.create_text(
                    x + 14,
                    y + 85 + j * 14,
                    text=line,
                    anchor="w",
                    fill="#eeeeee" if j < 6 else self.color_wave(j * 0.45 + i),
                    font=("Helvetica", 10, "bold" if j >= 6 else "normal")
                )

            # Mini coseno/seno visual en cada esquina
            mini_x = x + panel_w - 58
            mini_y = y + panel_h - 45
            mini_r = 26

            self.canvas.create_oval(
                mini_x - mini_r,
                mini_y - mini_r,
                mini_x + mini_r,
                mini_y + mini_r,
                outline=self.color_wave(i + 2),
                width=2
            )

            end_x = mini_x + math.cos(bm["theta"] + self.phase) * mini_r
            end_y = mini_y + math.sin(bm["theta"] + self.phase) * mini_r

            self.canvas.create_line(
                mini_x,
                mini_y,
                end_x,
                end_y,
                fill=self.color_wave(i + 4),
                width=3,
                capstyle=tk.ROUND
            )

            self.canvas.create_text(
                mini_x,
                mini_y + mini_r + 13,
                text="cos/sin",
                fill="#bbbbbb",
                font=("Helvetica", 9)
            )

    # -------------------------
    # Psicodelia visual
    # -------------------------
    def draw_background_spiral(self, cx, cy, w, h):
        max_radius = min(w, h) * 0.68

        for i in range(95):
            angle = self.phase * 0.65 + i * 0.28
            radius = i / 95 * max_radius

            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius

            size = 10 + 8 * math.sin(self.phase + i * 0.3)
            color = self.color_wave(i * 0.15)

            self.canvas.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
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
                x - size,
                y - size,
                x + size,
                y + size,
                fill=p["color"],
                outline=""
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
                x - size,
                y - size,
                x + size,
                y + size,
                outline=color,
                width=2
            )

    # -------------------------
    # Reloj
    # -------------------------
    def draw_clock_face(self, cx, cy, radius):
        for ring in range(5):
            extra = ring * 8 + 8 * math.sin(self.phase + ring)

            self.canvas.create_oval(
                cx - radius - extra,
                cy - radius - extra,
                cx + radius + extra,
                cy + radius + extra,
                outline=self.color_wave(ring * 0.7),
                width=2
            )

        for i in range(60):
            angle = math.tau * i / 60 - math.pi / 2

            if i % 5 == 0:
                length = 30
                width = 5
                color = self.color_wave(i * 0.2)
            else:
                length = 14
                width = 2
                color = "#555555"

            outer_x = cx + math.cos(angle) * radius
            outer_y = cy + math.sin(angle) * radius

            inner_x = cx + math.cos(angle) * (radius - length)
            inner_y = cy + math.sin(angle) * (radius - length)

            self.canvas.create_line(
                inner_x,
                inner_y,
                outer_x,
                outer_y,
                fill=color,
                width=width,
                capstyle=tk.ROUND
            )

        for i in range(1, 13):
            angle = math.tau * i / 12 - math.pi / 2
            x = cx + math.cos(angle) * (radius - 62)
            y = cy + math.sin(angle) * (radius - 62)

            color = self.color_wave(i * 0.6)

            self.canvas.create_text(
                x,
                y,
                text=str(i),
                fill=color,
                font=("Helvetica", 23, "bold")
            )

    def draw_hand(self, cx, cy, angle, length, width, color):
        x = cx + math.cos(angle) * length
        y = cy + math.sin(angle) * length

        for glow_width in range(width + 16, width, -4):
            self.canvas.create_line(
                cx,
                cy,
                x,
                y,
                fill=color,
                width=glow_width,
                capstyle=tk.ROUND,
                stipple="gray25"
            )

        self.canvas.create_line(
            cx,
            cy,
            x,
            y,
            fill=color,
            width=width,
            capstyle=tk.ROUND
        )

        self.canvas.create_oval(
            x - width * 1.35,
            y - width * 1.35,
            x + width * 1.35,
            y + width * 1.35,
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

        pulse = 16 + 8 * math.sin(self.phase * 4)

        self.canvas.create_oval(
            cx - pulse,
            cy - pulse,
            cx + pulse,
            cy + pulse,
            fill=self.color_wave(5),
            outline="white",
            width=2
        )

        time_text = now.strftime("%H:%M:%S")
        date_text = now.strftime("%A, %d %B %Y")

        self.canvas.create_text(
            cx,
            cy + radius + 52,
            text=time_text,
            fill=self.color_wave(2),
            font=("Helvetica", 46, "bold")
        )

        self.canvas.create_text(
            cx,
            cy + radius + 94,
            text=date_text,
            fill="#dddddd",
            font=("Helvetica", 18)
        )

    # -------------------------
    # Ayuda
    # -------------------------
    def draw_help(self, w, h):
        help_text = (
            "ESPACIO pausar | T estelas | P partículas | D normal | B Box-Muller | "
            "+ velocidad | - velocidad | R reset | ESC salir"
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
            150,
            375,
            text=f"{status}  |  velocidad x{self.speed:.1f}",
            fill=self.color_wave(1),
            font=("Helvetica", 14, "bold")
        )

    # -------------------------
    # Loop principal
    # -------------------------
    def animate(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        cx = w // 2
        cy = h // 2 - 55
        radius = min(w, h) * 0.265

        if not self.show_trails:
            self.canvas.delete("all")
        else:
            self.canvas.create_rectangle(
                0,
                0,
                w,
                h,
                fill="black",
                outline="",
                stipple="gray50"
            )

        if self.running:
            self.phase += 0.025 * self.speed

        self.draw_normal_distribution_background(w, h)
        self.draw_background_spiral(cx, cy, w, h)
        self.draw_particles(cx, cy)
        self.draw_mouse_vortex(cx, cy)
        self.draw_clock(cx, cy, radius)
        self.draw_distribution_stats(w, h)
        self.draw_box_muller_panels(w, h)
        self.draw_help(w, h)

        self.root.after(16, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = RelojPsicodelicoNormalBoxMuller(root)
    root.mainloop()
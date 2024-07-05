import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import pandas as pd
import time
from PIL import Image, ImageTk
import os
import numpy as np

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Página Principal")
        self.rows = 10
        self.cols = 10
        self.groups = 2
        self.selected_pins = {}
        self.current_color = tk.StringVar(value="")
        self.colors = [
            ("vermelho", "red"), ("verde", "green"), ("azul", "blue"), ("amarelo", "yellow"),
            ("laranja", "orange"), ("roxo", "purple"), ("rosa", "pink"), ("marrom", "brown"),
            ("preto", "black"), ("branco", "white"), ("ciano", "cyan"), ("magenta", "magenta"),
            ("limão", "lime"), ("bordô", "maroon"), ("marinho", "navy"), ("oliva", "olive"),
            ("verde-azulado", "teal"), ("violeta", "violet"), ("cinza", "gray"), ("ouro", "gold")
        ]
        self.selected_colors = [("vermelho", "red"), ("verde", "green")]  # Definindo cores padrão
        self.available_colors = self.colors[:]
        self.pin_size = 0
        self.zoom_factor = 1.0
        self.pin_coords = []
        self.original_pin_coords = {}  # To store original coordinates
        self.paths = []  # Store the paths for redrawing on resize
        self.init_setup_window()

    def init_setup_window(self):
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.title("Configurações Iniciais")

        tk.Label(self.setup_window, text="Quantidade de pinos por coluna:").pack()
        self.cols_entry = tk.Entry(self.setup_window)
        self.cols_entry.pack()
        self.cols_entry.insert(0, "10")

        tk.Label(self.setup_window, text="Quantidade de pinos por linha:").pack()
        self.rows_entry = tk.Entry(self.setup_window)
        self.rows_entry.pack()
        self.rows_entry.insert(0, "10")

        tk.Label(self.setup_window, text="Quantidade de grupos:").pack()
        self.groups_combobox = ttk.Combobox(self.setup_window, values=list(range(1, 21)))
        self.groups_combobox.pack()
        self.groups_combobox.set("2")
        self.groups_combobox.bind("<<ComboboxSelected>>", self.update_color_selection)

        self.color_frame = tk.Frame(self.setup_window)
        self.color_frame.pack()

        tk.Label(self.color_frame, text="Selecione as cores:").pack()

        self.color_comboboxes = []
        for color_name, _ in self.selected_colors:
            combobox = ttk.Combobox(self.color_frame, values=[color[0] for color in self.available_colors])
            combobox.pack(pady=5)
            combobox.set(color_name)
            combobox.bind("<<ComboboxSelected>>", self.update_color_options)
            self.color_comboboxes.append(combobox)

        tk.Button(self.setup_window, text="OK", command=self.process_setup).pack()

    def update_color_selection(self, event=None):
        for widget in self.color_frame.winfo_children():
            if isinstance(widget, ttk.Combobox):
                widget.destroy()

        self.color_comboboxes = []
        try:
            self.groups = int(self.groups_combobox.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, selecione um valor válido para a quantidade de grupos.")
            return

        self.selected_colors = self.selected_colors[:self.groups]
        self.available_colors = self.colors[:]

        for i in range(self.groups):
            color_name = self.selected_colors[i][0] if i < len(self.selected_colors) else ""
            combobox = ttk.Combobox(self.color_frame, values=[color[0] for color in self.available_colors])
            combobox.pack(pady=5)
            if color_name:
                combobox.set(color_name)
                self.available_colors.remove((color_name, next(code for name, code in self.colors if name == color_name)))
            combobox.bind("<<ComboboxSelected>>", self.update_color_options)
            self.color_comboboxes.append(combobox)

    def update_color_options(self, event=None):
        self.available_colors = self.colors[:]

        for combobox in self.color_comboboxes:
            selected_color = combobox.get()
            if selected_color:
                self.available_colors = [color for color in self.available_colors if color[0] != selected_color]

        for combobox in self.color_comboboxes:
            current_value = combobox.get()
            combobox['values'] = [color[0] for color in self.available_colors]
            if current_value:
                combobox.set(current_value)
                if current_value not in [color[0] for color in self.available_colors]:
                    combobox['values'] = [color[0] for color in self.colors]

        self.selected_colors = [(combobox.get(), next(code for name, code in self.colors if name == combobox.get())) for combobox in self.color_comboboxes if combobox.get()]

    def process_setup(self):
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())
            self.groups = int(self.groups_combobox.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos para linhas, colunas e grupos.")
            return

        self.selected_colors = []
        for combobox in self.color_comboboxes:
            color_name = combobox.get()
            if not color_name:
                messagebox.showerror("Erro", "Por favor, selecione uma cor para cada grupo.")
                return
            color_code = next((code for name, code in self.colors if name == color_name), None)
            if color_code:
                self.selected_colors.append((color_name, color_code))

        if len(set(self.selected_colors)) != self.groups:
            messagebox.showerror("Erro", "Cada grupo deve ter uma cor única selecionada.")
            return

        self.setup_window.destroy()
        self.init_main_window()
        self.root.deiconify()

    def init_main_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_menu()

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.current_color.set(self.selected_colors[0][1])
        self.draw_pins()

        color_frame = tk.Frame(self.root)
        color_frame.grid(row=2, column=0, pady=10)

        self.add_clear_button(color_frame)

        for color_name, color_code in self.selected_colors:
            tk.Radiobutton(color_frame, text=color_name, variable=self.current_color, value=color_code).pack(side=tk.LEFT, padx=5)

        tk.Button(self.root, text="Mostrar Pinos Selecionados", command=self.show_selected_pins).grid(row=3, column=0, pady=10)
        tk.Button(self.root, text="Traçar Caminhos", command=self.trace_paths).grid(row=4, column=0, pady=10)
        tk.Button(self.root, text="Calcular Gasto de Fios", command=self.calculate_wire_usage).grid(row=5, column=0, pady=10)

        zoom_frame = tk.Frame(self.root)
        zoom_frame.grid(row=0, column=0, pady=10)

        self.add_zoom_buttons(zoom_frame)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self.resize)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_zoom)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Configurações", command=self.show_setup_window)
        menu_bar.add_cascade(label="Opções", menu=settings_menu)

        zoom_menu = tk.Menu(menu_bar, tearoff=0)
        zoom_menu.add_command(label="Aumentar Zoom", command=lambda: self.zoom(1.1))
        zoom_menu.add_command(label="Diminuir Zoom", command=lambda: self.zoom(0.9))
        zoom_menu.add_command(label="Zoom Normal", command=self.reset_zoom)
        menu_bar.add_cascade(label="Zoom", menu=zoom_menu)

    def show_setup_window(self):
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.title("Configurações Iniciais")

        tk.Label(self.setup_window, text="Quantidade de pinos por coluna:").pack()
        self.cols_entry = tk.Entry(self.setup_window)
        self.cols_entry.pack()
        self.cols_entry.insert(0, str(self.cols))

        tk.Label(self.setup_window, text="Quantidade de pinos por linha:").pack()
        self.rows_entry = tk.Entry(self.setup_window)
        self.rows_entry.pack()
        self.rows_entry.insert(0, str(self.rows))

        tk.Label(self.setup_window, text="Quantidade de grupos:").pack()
        self.groups_combobox = ttk.Combobox(self.setup_window, values=list(range(1, 21)))
        self.groups_combobox.pack()
        self.groups_combobox.set(str(self.groups))
        self.groups_combobox.bind("<<ComboboxSelected>>", self.update_color_selection)

        self.color_frame = tk.Frame(self.setup_window)
        self.color_frame.pack()

        tk.Label(self.color_frame, text="Selecione as cores:").pack()

        self.color_comboboxes = []
        for color_name, _ in self.selected_colors:
            combobox = ttk.Combobox(self.color_frame, values=[color[0] for color in self.available_colors])
            combobox.pack(pady=5)
            combobox.set(color_name)
            combobox.bind("<<ComboboxSelected>>", self.update_color_options)
            self.color_comboboxes.append(combobox)

        tk.Button(self.setup_window, text="OK", command=self.process_setup).pack()

        self.update_color_selection()

    def add_clear_button(self, parent_frame):
        clear_icon = Image.open("eraser.png")  # Certifique-se de que o arquivo eraser.png esteja no mesmo diretório
        clear_icon = clear_icon.resize((20, 20), Image.Resampling.LANCZOS)
        clear_icon = ImageTk.PhotoImage(clear_icon)
        clear_button = tk.Button(parent_frame, image=clear_icon, command=self.clear_selection)
        clear_button.image = clear_icon  # Para evitar que a imagem seja coletada pelo garbage collector
        clear_button.pack(side=tk.LEFT, padx=5)

    def add_zoom_buttons(self, parent_frame):
        zoom_in_icon = Image.open("zoom_in.png")  # Certifique-se de que o arquivo zoom_in.png esteja no mesmo diretório
        zoom_in_icon = zoom_in_icon.resize((20, 20), Image.Resampling.LANCZOS)
        zoom_in_icon = ImageTk.PhotoImage(zoom_in_icon)
        zoom_in_button = tk.Button(parent_frame, image=zoom_in_icon, command=lambda: self.zoom(1.1))
        zoom_in_button.image = zoom_in_icon  # Para evitar que a imagem seja coletada pelo garbage collector
        zoom_in_button.pack(side=tk.LEFT, padx=5)

        zoom_reset_icon = Image.open("zoom_reset.png")  # Certifique-se de que o arquivo zoom_reset.png esteja no mesmo diretório
        zoom_reset_icon = zoom_reset_icon.resize((20, 20), Image.Resampling.LANCZOS)
        zoom_reset_icon = ImageTk.PhotoImage(zoom_reset_icon)
        zoom_reset_button = tk.Button(parent_frame, image=zoom_reset_icon, command=self.reset_zoom)
        zoom_reset_button.image = zoom_reset_icon  # Para evitar que a imagem seja coletada pelo garbage collector
        zoom_reset_button.pack(side=tk.LEFT, padx=5)

        zoom_out_icon = Image.open("zoom_out.png")  # Certifique-se de que o arquivo zoom_out.png esteja no mesmo diretório
        zoom_out_icon = zoom_out_icon.resize((20, 20), Image.Resampling.LANCZOS)
        zoom_out_icon = ImageTk.PhotoImage(zoom_out_icon)
        zoom_out_button = tk.Button(parent_frame, image=zoom_out_icon, command=lambda: self.zoom(0.9))
        zoom_out_button.image = zoom_out_icon  # Para evitar que a imagem seja coletada pelo garbage collector
        zoom_out_button.pack(side=tk.LEFT, padx=5)

    def clear_selection(self):
        color_code = self.current_color.get()
        pins_to_clear = [pin for pin in self.selected_pins if self.selected_pins[pin] == color_code]
        for pin in pins_to_clear:
            del self.selected_pins[pin]
            self.canvas.itemconfig(pin, fill="lightgrey")
        self.redraw_paths()

    def draw_pins(self):
        self.canvas.delete("all")
        total_width = self.canvas.winfo_width()
        total_height = self.canvas.winfo_height()

        max_pin_size = min(total_width // self.cols, total_height // self.rows)
        spacing = max_pin_size // 5
        self.pin_size = max_pin_size - spacing

        start_x = (total_width - (self.cols * self.pin_size + (self.cols - 1) * spacing)) // 2
        start_y = (total_height - (self.rows * self.pin_size + (self.rows - 1) * spacing)) // 2

        self.pin_coords = []  # Store coordinates of pins

        for i in range(self.rows):
            for j in range(self.cols):
                x0 = start_x + j * (self.pin_size + spacing)
                y0 = start_y + i * (self.pin_size + spacing)
                x1 = x0 + self.pin_size
                y1 = y0 + self.pin_size
                pin = self.canvas.create_oval(x0, y0, x1, y1, fill="lightgrey", outline="black")
                self.canvas.tag_bind(pin, "<Button-1>", self.on_pin_click)
                self.pin_coords.append((pin, (x0, y0, x1, y1)))  # Save pin and its coordinates
                self.original_pin_coords[pin] = (x0, y0, x1, y1)  # Save original coordinates

        self.restore_selected_pins()

    def restore_selected_pins(self):
        for pin, coords in self.pin_coords:
            if pin in self.selected_pins:
                self.canvas.itemconfig(pin, fill=self.selected_pins[pin])

    def on_pin_click(self, event):
        canvas = event.widget
        item = canvas.find_closest(event.x, event.y)[0]
        if item in self.selected_pins:
            del self.selected_pins[item]
            canvas.itemconfig(item, fill="lightgrey")
        else:
            self.selected_pins[item] = self.current_color.get()
            canvas.itemconfig(item, fill=self.current_color.get())

    def show_selected_pins(self):
        pins = [(self.canvas.coords(pin)[0] // (self.pin_size + self.pin_size // 5), self.canvas.coords(pin)[1] // (self.pin_size + self.pin_size // 5), self.get_color_name(self.canvas.itemcget(pin, "fill"))) for pin in self.selected_pins if self.canvas.coords(pin)]
        messagebox.showinfo("Pinos Selecionados", f"Você selecionou os seguintes pinos: {pins}")

    def get_color_name(self, color_code):
        return next((name for name, code in self.colors if code == color_code), color_code)

    def resize(self, event):
        self.adjust_pins()

    def adjust_pins(self):
        total_width = self.canvas.winfo_width()
        total_height = self.canvas.winfo_height()

        max_pin_size = min(total_width // self.cols, total_height // self.rows)
        spacing = max_pin_size // 5
        self.pin_size = max_pin_size - spacing

        start_x = (total_width - (self.cols * self.pin_size + (self.cols - 1) * spacing)) // 2
        start_y = (total_height - (self.rows * self.pin_size + (self.rows - 1) * spacing)) // 2

        for i, (pin, _) in enumerate(self.pin_coords):
            row = i // self.cols
            col = i % self.cols
            x0 = start_x + col * (self.pin_size + spacing) * self.zoom_factor
            y0 = start_y + row * (self.pin_size + spacing) * self.zoom_factor
            x1 = x0 + self.pin_size * self.zoom_factor
            y1 = y0 + self.pin_size * self.zoom_factor
            self.canvas.coords(pin, x0, y0, x1, y1)

        self.restore_selected_pins()
        self.redraw_paths()

    def pin_center(self, pin):
        x0, y0, x1, y1 = self.canvas.coords(pin)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def trace_paths(self):
        random.seed(42)  # Fixar a semente do gerador aleatório
        np.random.seed(42)  # Fixar a semente do gerador aleatório do numpy

        def firefly_algorithm(selected_pins, population_size=30, generations=100, gamma=1.0, beta0=2.0, alpha=0.2):
            fireflies = [np.array(random.sample(selected_pins.tolist(), len(selected_pins))) for _ in range(population_size)]
            best_firefly = fireflies[0]
            best_distance = fitness(best_firefly)

            for _ in range(generations):
                for i in range(population_size):
                    for j in range(population_size):
                        if fitness(fireflies[i]) > fitness(fireflies[j]):
                            fireflies[i] = move_firefly(fireflies[i], fireflies[j], alpha, beta0, gamma)
                    current_distance = fitness(fireflies[i])
                    if current_distance < best_distance:
                        best_firefly = fireflies[i]
                        best_distance = current_distance

            return best_firefly

        def fitness(path):
            return np.sum(np.linalg.norm(path[1:] - path[:-1], axis=1))

        def move_firefly(firefly1, firefly2, alpha, beta0, gamma):
            distance = fitness(firefly1)
            beta = beta0 * np.exp(-gamma * distance)
            new_firefly = firefly1 + beta * (firefly2 - firefly1) + alpha * (np.random.rand(*firefly1.shape) - 0.5)
            return new_firefly

        self.paths = []  # Clear previous paths
        self.canvas.delete("line")  # Clear previous lines

        results = []

        for color_name, color_code in self.selected_colors:
            selected_pins = [pin for pin in self.selected_pins if self.selected_pins[pin] == color_code]
            if len(selected_pins) < 2:
                continue  # Skip if less than two pins are selected for this color

            pin_centers = np.array([self.pin_center(pin) for pin in selected_pins])
            start_time = time.time()
            best_path = firefly_algorithm(pin_centers)
            end_time = time.time()
            elapsed_time = end_time - start_time
            total_distance = fitness(best_path)

            results.append({
                "Pins": len(selected_pins),
                "Distance": total_distance,
                "Time": elapsed_time,
                "Dimensions": f"{self.cols}x{self.rows}"
            })

            self.paths.append((selected_pins, best_path, color_code))  # Store the path for redrawing

            for i in range(len(best_path) - 1):
                self.canvas.create_line(best_path[i][0], best_path[i][1], best_path[i+1][0], best_path[i+1][1], fill=color_code, width=3, tags="line")  # Set the line width

        df = pd.DataFrame(results)
        file_exists = os.path.isfile("performance_results.csv")

        if file_exists:
            df.to_csv("performance_results.csv", mode='a', header=False, index=False)
        else:
            df.to_csv("performance_results.csv", mode='a', header=True, index=False)

        print(df)

    def redraw_paths(self):
        self.canvas.delete("line")  # Clear previous lines
        for selected_pins, path, color_code in self.paths:
            pin_centers = [self.pin_center(pin) for pin in selected_pins]
            for i in range(len(pin_centers) - 1):
                self.canvas.create_line(pin_centers[i][0], pin_centers[i][1], pin_centers[i+1][0], pin_centers[i+1][1], fill=color_code, width=3, tags="line")  # Set the line width

    def calculate_wire_usage(self):
        wire_lengths = {color: 0 for _, color in self.selected_colors}
        for _, path, color_code in self.paths:
            for i in range(len(path) - 1):
                wire_lengths[color_code] += math.sqrt((path[i+1][0] - path[i][0]) ** 2 + (path[i+1][1] - path[i][1]) ** 2)

        # Convert lengths from pixels to inches (considering 1 pixel = 0.1 inches for simplicity)
        pixel_to_inches = 2.54/26  # 1 pixel = 0.1 inches / 2.54 cm (1 inch = 2.54 cm)
        wire_lengths = {color: length * pixel_to_inches for color, length in wire_lengths.items()}

        wire_lengths_str = "\n".join([f"{self.get_color_name(color)}: {length:.2f} milimetros" for color, length in wire_lengths.items()])
        messagebox.showinfo("Gasto de Fios", f"Você gastou os seguintes comprimentos de fio:\n{wire_lengths_str}")

    def zoom(self, factor, focus_x=None, focus_y=None):
        self.zoom_factor *= factor
        if focus_x is not None and focus_y is not None:
            self.canvas.scale("all", focus_x, focus_y, factor, factor)
        self.adjust_pins()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.adjust_pins()

    def mouse_wheel_zoom(self, event):
        focus_x = self.canvas.canvasx(event.x)
        focus_y = self.canvas.canvasy(event.y)
        if event.delta > 0:
            self.zoom(1.1, focus_x, focus_y)
        elif event.delta < 0:
            self.zoom(0.9, focus_x, focus_y)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = App(root)
    root.mainloop()

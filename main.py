import tkinter as tk
from tkinter import simpledialog, colorchooser
from PIL import Image, ImageTk

class LogicGateSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("SAYISAL TASARIM PROJESİ")
        self.images = self.load_images()  # Initialize images before creating widgets
        self.create_widgets()
        self.gates = []
        self.inputs = []
        self.outputs = []
        self.connections = []
        self.nodes = []
        self.current_tool = None
        self.selected_element = None
        self.connection_start = None

    def create_widgets(self):
        # Araç çubuğu
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Mantık kapıları butonları
        for gate in ["AND", "OR", "NOT", "Buffer", "NAND", "NOR", "XOR", "XNOR"]:
            self.add_button(gate, self.toolbar, self.set_tool)

        # Giriş/Çıkış elemanları butonları
        self.add_button("Input Box", self.toolbar, self.set_tool)
        self.add_button("Output Box", self.toolbar, self.set_tool)
        self.add_button("LED", self.toolbar, self.set_tool)

        # Bağlantı elemanları butonları
        self.add_button("Connection", self.toolbar, self.set_tool)
        self.add_button("Connection Node", self.toolbar, self.set_tool)

        # Kontrol tuşları
        self.add_button("Run", self.toolbar, self.run_simulation, image=self.images["Run"])
        self.add_button("Reset", self.toolbar, self.reset_simulation, image=self.images["Reset"])
        self.add_button("Stop", self.toolbar, self.stop_simulation, image=self.images["Stop"])

        # Tasarım alanı
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<Button-3>", self.canvas_right_click)
        self.canvas.bind("<Control-Button-1>", self.canvas_right_click)

    def load_images(self):
        images = {}
        gates = ["AND", "OR", "NOT", "Buffer", "NAND", "NOR", "XOR", "XNOR"]
        elements = ["Input Box", "Output Box", "LED", "Connection Node", "Run", "Reset", "Stop"]
        for gate in gates:
            image = Image.open(f"{gate.lower()}_gate.png")
            images[gate] = ImageTk.PhotoImage(image)
        for elem in elements:
            image = Image.open(f"{elem.lower().replace(' ', '_')}.png")
            images[elem] = ImageTk.PhotoImage(image)
        return images

    def add_button(self, text, parent, command, image=None):
        if image:
            button = tk.Button(parent, text=text, command=lambda: command(), image=image, compound=tk.LEFT)
        else:
            button = tk.Button(parent, text=text, command=lambda: command(text))
        button.pack(side=tk.LEFT, padx=2, pady=2)

    def set_tool(self, tool):
        self.current_tool = tool

    def canvas_click(self, event):
        if self.current_tool == "Input Box":
            input_elem = InputElement(self.canvas, event.x, event.y, self.images["Input Box"])
            self.inputs.append(input_elem)
        elif self.current_tool == "Output Box":
            output_elem = OutputElement(self.canvas, event.x, event.y, self.images["Output Box"])
            self.outputs.append(output_elem)
        elif self.current_tool == "LED":
            led_elem = LEDElement(self.canvas, event.x, event.y, self.images["LED"])
            self.outputs.append(led_elem)
        elif self.current_tool in ["AND", "OR", "NOT", "Buffer", "NAND", "NOR", "XOR", "XNOR"]:
            gate = LogicGate(self.canvas, self.current_tool, event.x, event.y, self.images[self.current_tool])
            self.gates.append(gate)
        elif self.current_tool == "Connection":
            if self.connection_start is None:
                self.connection_start = (event.x, event.y)
            else:
                connection_end = (event.x, event.y)
                self.create_connection(self.connection_start, connection_end)
                self.connection_start = None
        elif self.current_tool == "Connection Node":
            node = ConnectionNode(self.canvas, event.x, event.y, self.images["Connection Node"])
            self.nodes.append(node)

    def canvas_right_click(self, event):
        element = self.find_element_at(event.x, event.y)
        if element:
            element.show_properties()

    def find_element_at(self, x, y):
        for gate in self.gates:
            if gate.contains_point(x, y):
                return gate
        for input_elem in self.inputs:
            if input_elem.contains_point(x, y):
                return input_elem
        for output_elem in self.outputs:
            if output_elem.contains_point(x, y):
                return output_elem
        for node in self.nodes:
            if node.contains_point(x, y):
                return node
        return None

    def create_connection(self, start, end):
        connection = Connection(self.canvas, start, end)
        self.connections.append(connection)

    def run_simulation(self):
        # Simülasyonu çalıştırma
        for gate in self.gates:
            gate.evaluate()
        for output_elem in self.outputs:
            output_elem.update_value()

    def reset_simulation(self):
        # Simülasyonu sıfırlama
        self.canvas.delete("all")
        self.gates.clear()
        self.inputs.clear()
        self.outputs.clear()
        self.connections.clear()
        self.nodes.clear()

    def stop_simulation(self):
        # Simülasyonu durdurma
        pass

class LogicGate:
    def __init__(self, canvas, gate_type, x, y, image):
        self.canvas = canvas
        self.gate_type = gate_type
        self.input_values = [0, 0]
        self.output_value = 0
        self.image = image
        self.representation = self.draw_gate(x, y)
        self.x, self.y = x, y
        self.properties = {"label": "", "inputs": 2}
        self.connections = []

    def draw_gate(self, x, y):
        return self.canvas.create_image(x - self.image.width() // 2, y - self.image.height() // 2, image=self.image, anchor=tk.NW)

    def contains_point(self, x, y):
        bbox = self.canvas.bbox(self.representation)
        return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

    def show_properties(self):
        label = simpledialog.askstring("Özellikler", "Etiket:", initialvalue=self.properties["label"])
        inputs = simpledialog.askinteger("Özellikler", "Giriş Sayısı:", initialvalue=self.properties["inputs"])
        if label is not None:
            self.properties["label"] = label
        if inputs is not None:
            self.properties["inputs"] = inputs

    def evaluate(self):
        # Mantık kapısının çıkış değerini hesaplama
        if self.gate_type == "AND":
            self.output_value = self.input_values[0] and self.input_values[1]
        elif self.gate_type == "OR":
            self.output_value = self.input_values[0] or self.input_values[1]
        elif self.gate_type == "NOT":
            self.output_value = not self.input_values[0]
        elif self.gate_type == "Buffer":
            self.output_value = self.input_values[0]
        elif self.gate_type == "NAND":
            self.output_value = not (self.input_values[0] and self.input_values[1])
        elif self.gate_type == "NOR":
            self.output_value = not (self.input_values[0] or self.input_values[1])
        elif self.gate_type == "XOR":
            self.output_value = self.input_values[0] != self.input_values[1]
        elif self.gate_type == "XNOR":
            self.output_value = self.input_values[0] == self.input_values[1]

    def add_connection(self, connection):
        self.connections.append(connection)

class InputElement:
    def __init__(self, canvas, x, y, image):
        self.canvas = canvas
        self.value = 0
        self.image = image
        self.representation = self.canvas.create_image(x, y, image=self.image, anchor=tk.CENTER)
        self.x, self.y = x, y
        self.properties = {"label": "", "color": "black", "initial_value": 0}
        self.connections = []

    def contains_point(self, x, y):
        bbox = self.canvas.bbox(self.representation)
        return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

    def show_properties(self):
        label = simpledialog.askstring("Özellikler", "Etiket:", initialvalue=self.properties["label"])
        color = colorchooser.askcolor(title="Renk Seç", initialcolor=self.properties["color"])[1]
        initial_value = simpledialog.askinteger("Özellikler", "Başlangıç Değeri:", initialvalue=self.properties["initial_value"])
        if label is not None:
            self.properties["label"] = label
        if color is not None:
            self.properties["color"] = color
        if initial_value is not None:
            self.properties["initial_value"] = initial_value

class OutputElement:
    def __init__(self, canvas, x, y, image):
        self.canvas = canvas
        self.value = 0
        self.image = image
        self.representation = self.canvas.create_image(x, y, image=self.image, anchor=tk.CENTER)
        self.x, self.y = x, y
        self.properties = {"label": "", "color": "black"}
        self.connections = []

    def contains_point(self, x, y):
        bbox = self.canvas.bbox(self.representation)
        return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

    def show_properties(self):
        label = simpledialog.askstring("Özellikler", "Etiket:", initialvalue=self.properties["label"])
        color = colorchooser.askcolor(title="Renk Seç", initialcolor=self.properties["color"])[1]
        if label is not None:
            self.properties["label"] = label
        if color is not None:
            self.properties["color"] = color

    def update_value(self):
        # Çıkış değerini güncelleme
        pass

class LEDElement(OutputElement):
    def __init__(self, canvas, x, y, image):
        super().__init__(canvas, x, y, image)

class Connection:
    def __init__(self, canvas, start, end):
        self.canvas = canvas
        self.start = start
        self.end = end
        self.line = self.draw_connection()

    def draw_connection(self):
        return self.canvas.create_line(self.start, self.end, fill="black")

class ConnectionNode:
    def __init__(self, canvas, x, y, image):
        self.canvas = canvas
        self.image = image
        self.representation = self.canvas.create_image(x, y, image=self.image, anchor=tk.CENTER)
        self.x, self.y = x, y
        self.connections = []

    def contains_point(self, x, y):
        bbox = self.canvas.bbox(self.representation)
        return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicGateSimulator(root)
    root.mainloop()

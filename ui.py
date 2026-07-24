import tkinter as tk


class MainWindow:

    def __init__(self):

        self.window = tk.Tk()

        self.window.title("PTG Digital Twin")

        self.window.geometry("500x500")

        self.window.resizable(False, False)

        title = tk.Label(
            self.window,
            text="PTG DIGITAL TWIN",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=15)

        self.rpm = tk.Label(self.window, text="RPM: 0", font=("Arial", 14))
        self.rpm.pack()

        self.current = tk.Label(self.window, text="Current: 0", font=("Arial", 14))
        self.current.pack()

        self.torque = tk.Label(self.window, text="Torque: 0", font=("Arial", 14))
        self.torque.pack()

        self.temperature = tk.Label(self.window, text="Temperature: 0", font=("Arial", 14))
        self.temperature.pack()

        self.error = tk.Label(self.window, text="Twin Error: 0", font=("Arial", 14))
        self.error.pack(pady=10)

        self.plus = tk.Button(
            self.window,
            text="+ Increase Load",
            width=20
        )

        self.plus.pack(pady=10)

        self.minus = tk.Button(
            self.window,
            text="- Decrease Load",
            width=20
        )

        self.minus.pack()

    def update_values(self, real, twin):

        self.rpm.config(text=f"RPM: {real['rpm']:.1f}")

        self.current.config(text=f"Current: {real['current']:.2f} A")

        self.torque.config(text=f"Torque: {real['torque']:.1f} Nm")

        self.temperature.config(text=f"Temperature: {real['temperature']:.2f} °C")

        error = abs(real["rpm"] - twin["rpm"])

        self.error.config(text=f"Twin Error: {error:.2f} rpm")
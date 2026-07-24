from ui import MainWindow
from motor import MotorSimulator
from digital_twin import DigitalTwin

window = MainWindow()

motor = MotorSimulator()
twin = DigitalTwin()


def update():

    real = motor.update()

    twin_data = twin.update(real)

    window.update_values(real, twin_data)

    window.window.after(200, update)


def increase():

    motor.increase_load()


def decrease():

    motor.decrease_load()


window.plus.config(command=increase)
window.minus.config(command=decrease)

update()

window.window.mainloop()
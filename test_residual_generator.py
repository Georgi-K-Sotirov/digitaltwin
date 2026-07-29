from core.residual_generator import ResidualGenerator

real = {
    "rpm": 1450,
    "current": 6.2,
    "temperature": 45,
    "voltage": 400,
    "frequency": 50,
    "torque": 15,
    "power": 2.2,
    "efficiency": 92,
}

predicted = {
    "rpm": 1448,
    "current": 6.0,
    "temperature": 44,
    "voltage": 399,
    "frequency": 50,
    "torque": 14.8,
    "power": 2.1,
    "efficiency": 91.5,
}

generator = ResidualGenerator()

residual = generator.calculate(real, predicted)

print("Тип:", type(residual))
print()
print("Обект:")
print(residual)
print()
print("Като речник:")
print(residual.to_dict())
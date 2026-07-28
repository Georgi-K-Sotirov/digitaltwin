from core.residual_generator import ResidualGenerator


measured = {
    "rpm": 1430,
    "current": 13.8,
    "temperature": 67.0,
}

predicted = {
    "rpm": 1460,
    "current": 12.5,
    "temperature": 62.0,
}

generator = ResidualGenerator()
result = generator.calculate(measured, predicted)

for key, value in result.items():
    print(f"{key}: {value}")
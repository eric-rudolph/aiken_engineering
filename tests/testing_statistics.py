import matplotlib.pyplot as plt

from engineering_tools.statistics.apply_statistics import NormalParameter, engineering_calculations


@engineering_calculations
def allowable_stress(yield_strength: float, safety_factor: float) -> float:
    return yield_strength / safety_factor


# the wrapped function still works like an ordinary function.
specified_result = allowable_stress(
    yield_strength=36_000.0,
    safety_factor=2.0,
)

print(f"Specified result: {specified_result}")

yield_strength = NormalParameter(specified=36_000.0,
                                 mean=42_000.0,
                                 standard_deviation=3_000.0,
                                 units="psi",
                                 label="Yield strength")

analysis = allowable_stress.analyze(
    parameters={"yield_strength": yield_strength},
    constants={"safety_factor": 2.0,},
    sample_count=100_000,
    random_seed=123,
    output_name="Allowable Stress",
    output_units="psi",
)

analysis.plot()
plt.show()

print(analysis.summary)





my_length = NormalParameter(specified=2.0, mean=2.1, standard_deviation=0.067, units="inch", label="Length")
my_height = NormalParameter(specified=5.0, mean=5.0, standard_deviation=0.12, units="inch", label="Height")

@engineering_calculations
def calculate_area(length: float, height: float) -> float:
    return length * height

my_results = calculate_area.analyze(
    parameters={"length": my_length,
                "height": my_height},
    sample_count=100_000,
)

my_results.plot()
plt.show()

print(my_results.summary.nominal_result)
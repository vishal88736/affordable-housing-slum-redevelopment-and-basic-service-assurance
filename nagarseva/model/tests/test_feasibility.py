from model.src.feasibility import simulate, sensitivity


def test_viable_project_has_positive_saleable_area():
    result = simulate({"land_area_sqm": 10_000, "fsi": 3, "eligible_households": 400})
    assert result["gross_built_up_area_sqft"] > result["free_rehab_area_sqft"]
    assert "verdict" in result
    assert len(sensitivity(result["inputs"])) == 5


def test_bad_inputs_are_rejected():
    try:
        simulate({"land_area_sqm": 0, "fsi": 2, "eligible_households": 10})
    except ValueError:
        pass
    else:
        raise AssertionError("zero land must be rejected")

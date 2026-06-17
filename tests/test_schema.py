from hydroreskit.schema import load_indicator_schema, validate_indicator_schema


def test_indicator_schema_validates():
    indicators = load_indicator_schema("configs/indicator_schema.yml")
    validate_indicator_schema(indicators)
    assert len(indicators) == 20


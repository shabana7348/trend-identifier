from app.data_processing import categorise_technology


def test_python_is_data_ai():
    assert categorise_technology("Python") == "Data/AI"


def test_ignores_capitals_and_spaces():
    assert categorise_technology("JAVASCRIPT") == "Web"
    assert categorise_technology("  Rust  ") == "Systems"


def test_c_plus_plus():
    assert categorise_technology("C++") == "Systems"


def test_unknown_language_is_other():
    assert categorise_technology("Cobol") == "Other"


def test_unknown_label_is_other():
    assert categorise_technology("Unknown") == "Other"


def test_empty_and_none_are_other():
    assert categorise_technology("") == "Other"
    assert categorise_technology(None) == "Other"
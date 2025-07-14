import pytest

from biocontext_kb.utils import slugify


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        ("Hello World", "hello-world"),
        ("Python is Awesome", "python-is-awesome"),
        ("Biocontext.AI 2025", "biocontext-ai-2025"),
        ("Special@Characters!", "special-characters-"),
        ("Spaces   in   between", "spaces---in---between"),
        ("", ""),
        ("12345", "12345"),
        ("__leading_and_trailing__", "--leading-and-trailing--"),
        (" Spaces to trim ", "spaces-to-trim"),
    ],
)
def test_slugify_conversion(input_name, expected_output):
    """Test that the slugify function properly converts strings to slugs."""
    result = slugify(input_name)
    assert result == expected_output

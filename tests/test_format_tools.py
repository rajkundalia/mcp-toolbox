"""
Tests for format conversion tools.

Tests both successful conversions and error handling for YAML/JSON tools.
"""

import pytest
import sys

sys.path.insert(0, 'server')

from tools.format_tools import yaml_to_json, json_to_yaml


class TestYamlToJson:
    """Test suite for yaml_to_json tool."""

    def test_simple_yaml(self):
        """Test basic YAML to JSON conversion."""
        yaml_input = """
name: John Doe
age: 30
"""
        result = yaml_to_json(yaml_input.strip())

        assert "json" in result
        assert "John Doe" in result["json"]
        assert "30" in result["json"]

    def test_nested_yaml(self):
        """Test nested YAML structure conversion."""
        yaml_input = """
person:
  name: Jane
  address:
    city: NYC
    zip: 10001
"""
        result = yaml_to_json(yaml_input.strip())

        assert "json" in result
        assert "person" in result["json"]
        assert "address" in result["json"]

    def test_yaml_list(self):
        """Test YAML list conversion."""
        yaml_input = """
skills:
  - Python
  - JavaScript
  - Docker
"""
        result = yaml_to_json(yaml_input.strip())

        assert "json" in result
        assert "Python" in result["json"]
        assert "[" in result["json"]  # JSON array syntax

    def test_empty_yaml(self):
        """Test empty YAML input."""
        result = yaml_to_json("")

        assert "json" in result
        # Empty YAML should produce null in JSON
        assert result["json"] == "null"

    def test_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        invalid_yaml = """
invalid: yaml: [[[
  - broken
"""
        with pytest.raises(ValueError) as excinfo:
            yaml_to_json(invalid_yaml)

        assert "Invalid YAML" in str(excinfo.value)

    def test_yaml_with_special_chars(self):
        """Test YAML with special characters."""
        yaml_input = """
message: "Hello, World!"
path: "/usr/local/bin"
"""
        result = yaml_to_json(yaml_input.strip())

        assert "json" in result
        assert "Hello, World!" in result["json"]


class TestJsonToYaml:
    """Test suite for json_to_yaml tool."""

    def test_simple_json(self):
        """Test basic JSON to YAML conversion."""
        json_input = '{"name": "John", "age": 30}'
        result = json_to_yaml(json_input)

        assert "yaml" in result
        assert "name: John" in result["yaml"] or "name: 'John'" in result["yaml"]
        assert "age: 30" in result["yaml"]

    def test_nested_json(self):
        """Test nested JSON structure conversion."""
        json_input = '''{
  "person": {
    "name": "Jane",
    "contacts": {
      "email": "jane@example.com"
    }
  }
}'''
        result = json_to_yaml(json_input)

        assert "yaml" in result
        assert "person:" in result["yaml"]
        assert "contacts:" in result["yaml"]

    def test_json_array(self):
        """Test JSON array conversion."""
        json_input = '{"skills": ["Python", "Go", "Rust"]}'
        result = json_to_yaml(json_input)

        assert "yaml" in result
        assert "skills:" in result["yaml"]
        assert "- Python" in result["yaml"]

    def test_empty_json_object(self):
        """Test empty JSON object."""
        result = json_to_yaml('{}')

        assert "yaml" in result
        assert result["yaml"].strip() == "{}"

    def test_invalid_json(self):
        """Test error handling for invalid JSON."""
        invalid_json = '{"broken": invalid}'

        with pytest.raises(ValueError) as excinfo:
            json_to_yaml(invalid_json)

        assert "Invalid JSON" in str(excinfo.value)

    def test_json_with_numbers(self):
        """Test JSON with various number types."""
        json_input = '{"int": 42, "float": 3.14, "negative": -10}'
        result = json_to_yaml(json_input)

        assert "yaml" in result
        assert "42" in result["yaml"]
        assert "3.14" in result["yaml"]

    def test_json_with_booleans(self):
        """Test JSON with boolean values."""
        json_input = '{"active": true, "deleted": false}'
        result = json_to_yaml(json_input)

        assert "yaml" in result
        # YAML represents booleans as true/false
        assert "true" in result["yaml"].lower()
        assert "false" in result["yaml"].lower()


class TestRoundTrip:
    """Test round-trip conversions (YAML -> JSON -> YAML)."""

    def test_yaml_json_yaml_roundtrip(self):
        """Test that YAML -> JSON -> YAML preserves data."""
        original_yaml = """
name: Alice
age: 25
active: true
"""
        # Convert to JSON
        json_result = yaml_to_json(original_yaml.strip())
        json_str = json_result["json"]

        # Convert back to YAML
        yaml_result = json_to_yaml(json_str)
        final_yaml = yaml_result["yaml"]

        # Check that key data is preserved
        assert "Alice" in final_yaml or "name: Alice" in final_yaml
        assert "25" in final_yaml

    def test_json_yaml_json_roundtrip(self):
        """Test that JSON -> YAML -> JSON preserves data."""
        import json

        original_data = {"name": "Bob", "score": 95}
        original_json = json.dumps(original_data)

        # Convert to YAML
        yaml_result = json_to_yaml(original_json)
        yaml_str = yaml_result["yaml"]

        # Convert back to JSON
        json_result = yaml_to_json(yaml_str)
        final_json = json_result["json"]

        # Parse and compare
        final_data = json.loads(final_json)
        assert final_data == original_data
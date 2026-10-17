"""Unit tests for Analytix safe XML loader."""

import io
import pytest

from src.xml_loader import (
    XMLEmptyError,
    XMLParsingError,
    load_xml_detailed,
)


def test_load_xml_valid():
    """Verify parsing repeating XML record elements into a DataFrame."""
    xml_data = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<students>\n"
        '    <student id="101">\n'
        "        <name>Alice</name>\n"
        "        <major>Computer Science</major>\n"
        "        <gpa>3.92</gpa>\n"
        "    </student>\n"
        '    <student id="102">\n'
        "        <name>Bob</name>\n"
        "        <major>Data Analytics</major>\n"
        "        <gpa>3.75</gpa>\n"
        "    </student>\n"
        "</students>\n"
    ).encode("utf-8")

    res = load_xml_detailed(io.BytesIO(xml_data))
    assert len(res.df) == 2
    assert "name" in res.df.columns
    assert "major" in res.df.columns
    assert "@id" in res.df.columns
    assert res.df["name"].iloc[0] == "Alice"


def test_load_xml_security_blocks_xxe():
    """Verify malicious DOCTYPE/ENTITY declarations are blocked for security."""
    malicious_xml = (
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE root [\n'
        '  <!ENTITY xxe SYSTEM "file:///etc/passwd">\n'
        ']>\n'
        '<root>&xxe;</root>'
    ).encode("utf-8")

    with pytest.raises(XMLParsingError) as exc_info:
        load_xml_detailed(io.BytesIO(malicious_xml))
    assert "security check failed" in str(exc_info.value).lower()


def test_load_xml_empty_error():
    """Verify empty XML raises XMLEmptyError."""
    with pytest.raises(XMLEmptyError):
        load_xml_detailed(io.BytesIO(b""))


def test_load_xml_malformed_syntax():
    """Verify unclosed tag raises XMLParsingError."""
    with pytest.raises(XMLParsingError):
        load_xml_detailed(io.BytesIO(b"<root><item>test</root>"))

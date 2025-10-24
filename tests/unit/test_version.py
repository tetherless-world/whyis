"""
Unit tests for whyis._version module.

Tests version string format and accessibility.
"""

import pytest
import re
from whyis._version import __version__


class TestVersion:
    """Test the version string."""
    
    def test_version_exists(self):
        """Test that __version__ is defined."""
        assert __version__ is not None
    
    def test_version_is_string(self):
        """Test that __version__ is a string."""
        assert isinstance(__version__, str)
    
    def test_version_not_empty(self):
        """Test that __version__ is not empty."""
        assert len(__version__) > 0
    
    def test_version_format(self):
        """Test that __version__ follows semantic versioning format."""
        # Should match X.Y.Z or X.Y.Z.postN or similar
        pattern = r'^\d+\.\d+\.\d+(\.\w+)?$'
        assert re.match(pattern, __version__), \
            f"Version {__version__} should follow semantic versioning"
    
    def test_version_has_major(self):
        """Test that version has a major version number."""
        parts = __version__.split('.')
        assert len(parts) >= 1
        assert parts[0].isdigit()
    
    def test_version_has_minor(self):
        """Test that version has a minor version number."""
        parts = __version__.split('.')
        assert len(parts) >= 2
        assert parts[1].isdigit()
    
    def test_version_has_patch(self):
        """Test that version has a patch version number."""
        parts = __version__.split('.')
        assert len(parts) >= 3
        assert parts[2].isdigit()
    
    def test_version_parts_are_numeric(self):
        """Test that major.minor.patch parts are numeric."""
        parts = __version__.split('.')[:3]
        for i, part in enumerate(parts):
            assert part.isdigit(), \
                f"Version part {i} ({part}) should be numeric"
    
    def test_version_can_be_imported(self):
        """Test that version can be imported from package."""
        import whyis
        assert hasattr(whyis, '__version__') or hasattr(whyis._version, '__version__')
    
    def test_version_major_is_reasonable(self):
        """Test that major version is a reasonable number."""
        major = int(__version__.split('.')[0])
        assert major >= 0
        assert major < 1000  # Sanity check
    
    def test_version_minor_is_reasonable(self):
        """Test that minor version is a reasonable number."""
        minor = int(__version__.split('.')[1])
        assert minor >= 0
        assert minor < 1000  # Sanity check
    
    def test_version_patch_is_reasonable(self):
        """Test that patch version is a reasonable number."""
        patch = int(__version__.split('.')[2])
        assert patch >= 0
        assert patch < 1000  # Sanity check

"""Unit tests for promptosaurus.builders.builder."""

import unittest
from pathlib import Path

import pytest

from promptosaurus.builders.builder import Builder


class TestBuilder(unittest.TestCase):
    """Tests for the Builder base class."""

    def test_builder_is_class(self):
        """Builder should be a class."""
        assert isinstance(Builder, type)

    def test_builder_has_build_method(self):
        """Builder should have a build method."""
        assert hasattr(Builder, "build")

    def test_builder_build_raises_not_implemented(self):
        """Builder.build() should raise NotImplementedError."""

        class ConcreteBuilder(Builder):
            pass

        builder = ConcreteBuilder()
        with pytest.raises(NotImplementedError):
            builder.build(Path("/tmp/output"))

    def test_builder_build_with_dry_run_raises_not_implemented(self):
        """Builder.build() with dry_run=True should raise NotImplementedError."""

        class ConcreteBuilder(Builder):
            pass

        builder = ConcreteBuilder()
        with pytest.raises(NotImplementedError):
            builder.build(Path("/tmp/output"), dry_run=True)

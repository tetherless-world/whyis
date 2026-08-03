"""Dependency-free replacements for the ``pkg_resources`` resource helpers.

``pkg_resources`` (shipped with setuptools) is deprecated and is no longer
guaranteed to be importable on Python 3.12+, where setuptools is not part of a
default environment. Whyis is always installed as a regular directory on disk
(never as a zipped egg), so we can resolve package resources directly from the
filesystem via :mod:`importlib`. These functions mirror the small subset of the
``pkg_resources`` API that Whyis relies on.
"""

import importlib.util
import os

__all__ = [
    "resource_filename",
    "resource_listdir",
    "resource_string",
    "resource_exists",
    "resource_stream",
]


def _base_dir(package):
    """Return the on-disk directory associated with a package or module name.

    For a package (e.g. ``"whyis"``) this is the package directory. For a
    module (e.g. ``"whyis.fuseki.fuseki"``) it is the directory containing the
    module file, matching ``pkg_resources`` resource-resolution semantics.
    """
    spec = importlib.util.find_spec(package)
    if spec is None:
        raise ModuleNotFoundError(f"No module named {package!r}")
    if spec.submodule_search_locations:
        return list(spec.submodule_search_locations)[0]
    if spec.origin and spec.origin not in ("built-in", "frozen"):
        return os.path.dirname(spec.origin)
    raise ValueError(f"Cannot determine a resource directory for {package!r}")


def resource_filename(package, resource=""):
    """Return the filesystem path to ``resource`` within ``package``."""
    base = _base_dir(package)
    if not resource:
        return base
    return os.path.join(base, *resource.split("/"))


def resource_listdir(package, resource):
    """List the contents of a directory ``resource`` within ``package``."""
    return os.listdir(resource_filename(package, resource))


def resource_string(package, resource):
    """Return the contents of ``resource`` within ``package`` as bytes."""
    with open(resource_filename(package, resource), "rb") as handle:
        return handle.read()


def resource_exists(package, resource):
    """Return whether ``resource`` exists within ``package``."""
    return os.path.exists(resource_filename(package, resource))


def resource_stream(package, resource):
    """Open ``resource`` within ``package`` as a binary stream."""
    return open(resource_filename(package, resource), "rb")

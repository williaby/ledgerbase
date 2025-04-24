noxfile.py
==========

**Description**: Nox sessions for testing, linting, CI, and documentation generation in LedgerBase.

.. automodule:: noxfile
   :members:
   :undoc-members:
   :show-inheritance:

**Usage**::

   nox -s <session_name> (e.g., nox -s tests)

**Behavior**:
Defines reusable Nox sessions for CI workflows such as linting, testing, doc building, and security scans.

**Dependencies**:
- nox
- poetry
----

*Note:* This module should define `__all__` to ensure Sphinx can document it correctly.
Consider also using docstrings on all public members for best results.

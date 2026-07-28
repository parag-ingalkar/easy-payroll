"""Shared pytest fixtures for the easy-payroll backend.

The payroll calculation engine is pure Python (no DB/HTTP), so the engine
unit tests under ``tests/features/payroll/domain/`` need no fixtures. This
file exists to anchor the ``tests`` package and to host shared fixtures as
integration tests are added later.
"""

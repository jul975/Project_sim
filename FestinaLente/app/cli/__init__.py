"""Command-line interface package for execution request entrypoints.

This package owns user-facing CLI concerns such as argument parsing,
interactive menu input, request construction, and top-level dispatch into
the execution layer. It should remain free of workflow execution,
simulation logic, and analytics processing.
"""

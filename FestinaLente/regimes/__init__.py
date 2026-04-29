"""Regime definitions, registries, and compilation entry points.

The regimes package separates human-authored ecological specifications from the
compiled parameter bundles consumed by the engine.

core.laws has no dependency on regimes, engine, or Agent.

regimes can import core.laws.

Agent can import core.laws or receive results from domain services.

Engine should mostly orchestrate, not implement laws.
"""

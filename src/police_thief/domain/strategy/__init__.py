"""The strategy module: the boundary between transport and a thinking agent.

docs/tasks.md Sec. 6.1: connects to the runtime immediately after hint
decoding and before Commit packaging. Concrete brains are selected via the
private per-peer config's [strategy] cop_class/thief_class key
(shared/config.py::load_strategy_class), never hardcoded into the
transport layer.
"""

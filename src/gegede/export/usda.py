'''Shim so that `gegede -o foo.usda` resolves to the usd exporter.'''
from gegede.export.usd import *  # noqa: F401,F403

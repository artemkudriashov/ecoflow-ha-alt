"""Protobuf support for EcoFlow devices."""
from .alternator_pb import get_alternator_protobuf

__all__ = ['get_alternator_protobuf', 'encode_alternator_command']
from .alternator_pb import encode_alternator_command

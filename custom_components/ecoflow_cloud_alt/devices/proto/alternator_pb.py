"""Protobuf decoder for Alternator Charger."""
import logging
from google.protobuf import message
from google.protobuf.descriptor import FieldDescriptor

_LOGGER = logging.getLogger(__name__)


# Protobuf schema as Python string (embedded, no need for .proto file compilation)
ALTERNATOR_PROTO = """
syntax = "proto3";

message AlternatorHeartbeat {
    optional int32 status1 = 1;
    optional int32 temp = 102;
    optional float alternatorPower = 105;
    optional int32 switchOFF130 = 130;
    optional int32 startVoltage = 138;
    optional float carBatVolt = 139;
    optional float batSoc = 262;
    optional int32 chargeToFull268 = 268;
    optional int32 unknown269 = 269;
    optional float stationPower = 425;
    optional int32 unknown427 = 427;
    optional int32 unknown428 = 428;
    optional int32 operationMode = 581;
    optional int32 startStop = 597;
    optional float permanentWatts = 598;
    optional float wifiRssi = 602;
    optional float ratedPower = 603;
    optional float cableLength608 = 608;
    optional float unknown609 = 609;
}

message HeartbeatHeader {
    AlternatorHeartbeat pdata = 1;
    int32 src = 2;
    int32 dest = 3;
    int32 d_src = 4;
    int32 d_dest = 5;
    int32 cmd_func = 8;
    int32 cmd_id = 9;
    int32 data_len = 10;
    int32 need_ack = 11;
    int32 is_ack = 12;
    int32 seq = 14;
    int32 product_id = 15;
    int32 version = 16;
    int32 payload_ver = 17;
}

message HeartbeatMessage {
    HeartbeatHeader header = 1;
}
"""


class AlternatorProtobuf:
    """Protobuf decoder for Alternator Charger."""

    def __init__(self):
        """Initialize protobuf types."""
        from google.protobuf import descriptor_pb2, symbol_database
        from google.protobuf.descriptor_pool import DescriptorPool
        
        # Parse proto string
        try:
            import tempfile
            import os
            from google.protobuf.compiler import parser
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.proto', delete=False) as f:
                f.write(ALTERNATOR_PROTO)
                proto_file = f.name
            
            try:
                # Parse proto file
                with open(proto_file, 'r') as f:
                    parsed = parser.parse(f.read())
                    
                self.pool = DescriptorPool()
                self.db = symbol_database.Default()
                
                _LOGGER.debug("Alternator protobuf schema loaded")
            finally:
                os.unlink(proto_file)
                
        except Exception as e:
            _LOGGER.error(f"Failed to initialize Alternator protobuf: {e}")
            self.pool = None
            self.db = None

    def decode_heartbeat(self, data: bytes) -> dict:
        """Decode Alternator Charger heartbeat protobuf message.
        
        Args:
            data: Raw protobuf bytes from MQTT
            
        Returns:
            Dictionary with decoded data or empty dict on error
        """
        if not data:
            return {}
            
        try:
            # Try to decode as raw protobuf message without schema
            # This is a fallback when proto compilation fails
            result = self._decode_raw_protobuf(data)
            
            if result:
                _LOGGER.debug(f"Decoded Alternator heartbeat: {result}")
                return result
            else:
                _LOGGER.warning("Failed to decode Alternator heartbeat")
                return {}
                
        except Exception as e:
            _LOGGER.error(f"Error decoding Alternator protobuf: {e}")
            return {}

    def _decode_raw_protobuf(self, data: bytes) -> dict:
        """Decode protobuf without compiled schema using field numbers."""
        result = {}
        
        try:
            # Protobuf wire format decoder
            from google.protobuf.internal import decoder, wire_format
            
            pos = 0
            while pos < len(data):
                # Read tag (field number + wire type)
                tag_bytes = []
                while True:
                    if pos >= len(data):
                        break
                    b = data[pos]
                    tag_bytes.append(b)
                    pos += 1
                    if not (b & 0x80):
                        break
                
                if not tag_bytes:
                    break
                    
                tag = 0
                for i, b in enumerate(tag_bytes):
                    tag |= (b & 0x7f) << (7 * i)
                
                field_number = tag >> 3
                wire_type = tag & 0x7
                
                # Decode value based on wire type
                if wire_type == 0:  # Varint (int32, bool)
                    value_bytes = []
                    while pos < len(data):
                        b = data[pos]
                        value_bytes.append(b)
                        pos += 1
                        if not (b & 0x80):
                            break
                    
                    value = 0
                    for i, b in enumerate(value_bytes):
                        value |= (b & 0x7f) << (7 * i)
                    
                    # Map field numbers to known fields
                    field_map = {
                        1: 'status1',
                        102: 'temp',
                        130: 'switchOFF130',
                        138: 'startVoltage',
                        262: 'batSoc',
                        268: 'chargeToFull268',
                        269: 'unknown269',
                        427: 'unknown427',
                        428: 'unknown428',
                        581: 'operationMode',
                        597: 'startStop',
                    }
                    
                    if field_number in field_map:
                        result[field_map[field_number]] = value
                        
                elif wire_type == 1:  # 64-bit (fixed64, double)
                    if pos + 8 <= len(data):
                        pos += 8
                        
                elif wire_type == 2:  # Length-delimited (string, bytes, embedded messages)
                    # Read length
                    length_bytes = []
                    while pos < len(data):
                        b = data[pos]
                        length_bytes.append(b)
                        pos += 1
                        if not (b & 0x80):
                            break
                    
                    length = 0
                    for i, b in enumerate(length_bytes):
                        length |= (b & 0x7f) << (7 * i)
                    
                    # Read data
                    if pos + length <= len(data):
                        value_data = data[pos:pos + length]
                        pos += length
                        
                        # If field 1 (nested pdata), recursively decode
                        if field_number == 1:
                            nested = self._decode_raw_protobuf(value_data)
                            result.update(nested)
                            
                elif wire_type == 5:  # 32-bit (fixed32, float)
                    if pos + 4 <= len(data):
                        import struct
                        float_bytes = data[pos:pos + 4]
                        value = struct.unpack('<f', float_bytes)[0]
                        pos += 4
                        
                        # Map float fields
                        float_map = {
                            105: 'alternatorPower',
                            139: 'carBatVolt',
                            425: 'stationPower',
                            598: 'permanentWatts',
                            602: 'wifiRssi',
                            603: 'ratedPower',
                            608: 'cableLength608',
                            609: 'unknown609',
                        }
                        
                        if field_number in float_map:
                            result[float_map[field_number]] = value
                else:
                    # Unknown wire type, skip
                    break
            
            # Convert special fields
            if 'startVoltage' in result:
                result['startVoltage'] = result['startVoltage'] / 10.0
                
            return result
            
        except Exception as e:
            _LOGGER.debug(f"Raw protobuf decode error: {e}")
            return {}


# Global instance
_alternator_proto = None


def get_alternator_protobuf():
    """Get or create Alternator protobuf decoder."""
    global _alternator_proto
    if _alternator_proto is None:
        _alternator_proto = AlternatorProtobuf()
    return _alternator_proto

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

    def decode_heartbeat(self, data: bytes, seq: int = None) -> dict:
        """Decode Alternator Charger heartbeat protobuf message.
        
        Args:
            data: Raw protobuf bytes from MQTT (may be encrypted)
            seq: Sequence number from MQTT header (for XOR decryption)
            
        Returns:
            Dictionary with decoded data or empty dict on error
        """
        if not data:
            return {}
            
        try:
            # Alternator Charger uses XOR encryption with sequence number
            # Check if data looks encrypted (encType == 1)
            decrypted_data = data
            
            if seq is not None:
                # Command responses have timestamp seq (large), heartbeats have counter (small)
                if seq > 100000000:
                    # Command response - try raw decode first (no XOR)
                    _LOGGER.debug(f"Command response detected (seq={seq}), trying raw decode")
                    result = self._decode_raw_protobuf(data)
                    if result:
                        _LOGGER.debug(f"Decoded command response: {result}")
                        return result
                    # Fallback to XOR if raw failed
                    _LOGGER.debug("Raw decode failed, trying XOR")
                    decrypted_data = bytes([b ^ seq for b in data])
                else:
                    # Heartbeat - use XOR decryption
                    _LOGGER.debug(f"Attempting XOR decryption with seq={seq}")
                    decrypted_data = bytes([b ^ seq for b in data])
            
            # Try to decode as raw protobuf message without schema
            result = self._decode_raw_protobuf(decrypted_data)
            
            if result:
                _LOGGER.debug(f"Decoded Alternator heartbeat: {result}")
                return result
            else:
                # If decryption failed, try without decryption
                if seq is not None:
                    _LOGGER.debug("XOR decryption failed, trying raw data")
                    result = self._decode_raw_protobuf(data)
                    if result:
                        return result
                
                _LOGGER.warning("Failed to decode Alternator heartbeat")
                return {}
                
        except Exception as e:
            _LOGGER.error(f"Error decoding Alternator protobuf: {e}")
            return {}

    def _decode_raw_protobuf(self, data: bytes) -> dict:
        """Decode protobuf without compiled schema using field numbers."""
        result = {}
        seq_number = None
        
        try:
            # First, try to extract sequence number from header (field 14)
            # and encrypted pdata (field 1) if this is a full message
            header_data = None
            pdata = None
            
            temp_pos = 0
            while temp_pos < len(data):
                try:
                    tag_bytes = []
                    while temp_pos < len(data):
                        b = data[temp_pos]
                        tag_bytes.append(b)
                        temp_pos += 1
                        if not (b & 0x80):
                            break
                    
                    if not tag_bytes:
                        break
                    
                    tag = 0
                    for i, b in enumerate(tag_bytes):
                        tag |= (b & 0x7f) << (7 * i)
                    
                    field_number = tag >> 3
                    wire_type = tag & 0x7
                    
                    # If field 1 (pdata - nested message)
                    if field_number == 1 and wire_type == 2:
                        # Read length
                        length_bytes = []
                        while temp_pos < len(data):
                            b = data[temp_pos]
                            length_bytes.append(b)
                            temp_pos += 1
                            if not (b & 0x80):
                                break
                        
                        length = 0
                        for i, b in enumerate(length_bytes):
                            length |= (b & 0x7f) << (7 * i)
                        
                        if temp_pos + length <= len(data):
                            pdata = data[temp_pos:temp_pos + length]
                            temp_pos += length
                    
                    # If field 14 (seq - varint)
                    elif field_number == 14 and wire_type == 0:
                        value_bytes = []
                        while temp_pos < len(data):
                            b = data[temp_pos]
                            value_bytes.append(b)
                            temp_pos += 1
                            if not (b & 0x80):
                                break
                        
                        seq_number = 0
                        for i, b in enumerate(value_bytes):
                            seq_number |= (b & 0x7f) << (7 * i)
                        
                        _LOGGER.debug(f"Found seq={seq_number} in protobuf header")
                    
                    else:
                        # Skip other fields
                        if wire_type == 0:  # Varint
                            while temp_pos < len(data):
                                b = data[temp_pos]
                                temp_pos += 1
                                if not (b & 0x80):
                                    break
                        elif wire_type == 1:  # 64-bit
                            temp_pos += 8
                        elif wire_type == 2:  # Length-delimited
                            length_bytes = []
                            while temp_pos < len(data):
                                b = data[temp_pos]
                                length_bytes.append(b)
                                temp_pos += 1
                                if not (b & 0x80):
                                    break
                            
                            length = 0
                            for i, b in enumerate(length_bytes):
                                length |= (b & 0x7f) << (7 * i)
                            
                            temp_pos += length
                        elif wire_type == 5:  # 32-bit
                            temp_pos += 4
                except:
                    break
            
            # If we found encrypted pdata and seq, decrypt it (only for heartbeats)
            if pdata and seq_number is not None:
                # Command responses have large seq (timestamp), heartbeats have small seq
                if seq_number > 100000000:
                    # Command response - NO decryption
                    _LOGGER.debug(f"Command response detected (seq={seq_number}), using raw pdata")
                    data = pdata
                else:
                    # Heartbeat - decrypt with XOR
                    _LOGGER.debug(f"Decrypting pdata with seq={seq_number}")
                    pdata = bytes([b ^ (seq_number & 0xFF) for b in pdata])
                    data = pdata  # Use decrypted data for actual parsing
            
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
                            field_name = float_map[field_number]
                            # Invert sign for power fields (EcoFlow reports output as negative)
                            if field_name in ['alternatorPower', 'stationPower']:
                                result[field_name] = -value
                            else:
                                result[field_name] = value
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




def encode_alternator_command(params: dict) -> bytes:
    """Encode Alternator Charger command to protobuf format (full setMessage)."""
    import time
    import struct
    import logging
    
    _LOGGER = logging.getLogger(__name__)
    
    seq = int(time.time() * 1000)
    
    # Field map for alternatorSet (pdata)
    pdata_field_map = {
        'switchOFF130': 1,
        'operationMode': 116,
        'startStop': 122,
        'permanentWatts': 123,
        'startVoltage': 137,
        'cableLength608': 203
    }
    
    def encode_varint(value):
        """Encode integer as protobuf varint."""
        result = []
        value = int(value) & 0xFFFFFFFF
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    def encode_string(s):
        """Encode string as length-delimited."""
        s_bytes = s.encode('utf-8')
        return encode_varint(len(s_bytes)) + s_bytes
    
    # Build alternatorSet (pdata)
    pdata_bytes = bytearray()
    for key, value in params.items():
        if key in pdata_field_map:
            field_num = pdata_field_map[key]
            if key in ['permanentWatts', 'cableLength608']:
                # Float (wire type 5)
                tag = (field_num << 3) | 5
                pdata_bytes.extend(encode_varint(tag))
                pdata_bytes.extend(struct.pack('<f', float(value)))
            elif key == 'startVoltage':
                # Int32 (wire type 0) - multiply by 10
                tag = (field_num << 3) | 0
                pdata_bytes.extend(encode_varint(tag))
                pdata_bytes.extend(encode_varint(int(value * 10)))
            else:
                # Int32 (wire type 0)
                tag = (field_num << 3) | 0
                pdata_bytes.extend(encode_varint(tag))
                pdata_bytes.extend(encode_varint(int(value)))
    
    # Calculate dataLen based on pdata content
    if 'permanentWatts' in params or 'cableLength608' in params:
        data_len = 6
    elif 'startVoltage' in params:
        data_len = 4
    else:
        data_len = 3
    
    # Build setHeader
    header_bytes = bytearray()
    
    # Field 1: pdata (alternatorSet) - length-delimited
    header_bytes.extend(encode_varint((1 << 3) | 2))
    header_bytes.extend(encode_varint(len(pdata_bytes)))
    header_bytes.extend(pdata_bytes)
    
    # Field 2: src = 32
    header_bytes.extend(encode_varint((2 << 3) | 0))
    header_bytes.extend(encode_varint(32))
    
    # Field 3: dest = 20
    header_bytes.extend(encode_varint((3 << 3) | 0))
    header_bytes.extend(encode_varint(20))
    
    # Field 4: d_src = 1
    header_bytes.extend(encode_varint((4 << 3) | 0))
    header_bytes.extend(encode_varint(1))
    
    # Field 5: d_dest = 1
    header_bytes.extend(encode_varint((5 << 3) | 0))
    header_bytes.extend(encode_varint(1))
    
    # Field 6: enc_type = 1
    header_bytes.extend(encode_varint((6 << 3) | 0))
    header_bytes.extend(encode_varint(1))
    
    # Field 7: check_type = 3
    header_bytes.extend(encode_varint((7 << 3) | 0))
    header_bytes.extend(encode_varint(3))
    
    # Field 8: cmd_func = 254
    header_bytes.extend(encode_varint((8 << 3) | 0))
    header_bytes.extend(encode_varint(254))
    
    # Field 9: cmd_id = 17
    header_bytes.extend(encode_varint((9 << 3) | 0))
    header_bytes.extend(encode_varint(17))
    
    # Field 10: data_len
    header_bytes.extend(encode_varint((10 << 3) | 0))
    header_bytes.extend(encode_varint(data_len))
    
    # Field 11: need_ack = 1
    header_bytes.extend(encode_varint((11 << 3) | 0))
    header_bytes.extend(encode_varint(1))
    
    # Field 14: seq (timestamp)
    header_bytes.extend(encode_varint((14 << 3) | 0))
    header_bytes.extend(encode_varint(seq))
    
    # Field 16: version = 19
    header_bytes.extend(encode_varint((16 << 3) | 0))
    header_bytes.extend(encode_varint(19))
    
    # Field 17: payload_ver = 1
    header_bytes.extend(encode_varint((17 << 3) | 0))
    header_bytes.extend(encode_varint(1))
    
    # Field 23: from = "Android"
    header_bytes.extend(encode_varint((23 << 3) | 2))
    header_bytes.extend(encode_string("Android"))
    
    # Build setMessage (field 1 = setHeader)
    message_bytes = bytearray()
    message_bytes.extend(encode_varint((1 << 3) | 2))  # Field 1, wire type 2
    message_bytes.extend(encode_varint(len(header_bytes)))
    message_bytes.extend(header_bytes)
    
    _LOGGER.debug(f"Encoded Alternator command (full setMessage): {params} -> {len(message_bytes)} bytes")
    return bytes(message_bytes)


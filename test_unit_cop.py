#!/usr/bin/env python3
"""Test script to check Unit_COP register format."""
import struct

# Test both interpretations:

# Option 1: Unit_COP as single 16-bit register with 0.1 precision
def test_16bit_cop(reg_value):
    """Test as 16-bit signed int with 0.1 precision."""
    if reg_value > 32767:
        reg_value = reg_value - 65536
    cop = float(reg_value / 10)
    print(f"16-bit interpretation: register={reg_value} -> COP={cop}")
    return cop

# Option 2: Unit_COP as 32-bit float (2 registers: 389-390)
def test_32bit_cop(high_reg, low_reg):
    """Test as 32-bit IEEE 754 float."""
    # Ensure values are unsigned 16-bit
    high_reg = high_reg & 0xFFFF
    low_reg = low_reg & 0xFFFF
    # Combine into 32-bit integer (big-endian order)
    combined = (high_reg << 16) | low_reg
    # Convert to float
    try:
        cop = struct.unpack('>f', struct.pack('>I', combined))[0]
        print(f"32-bit float interpretation: high={high_reg:04X} low={low_reg:04X} -> COP={cop}")
        return cop
    except:
        print(f"32-bit float interpretation: FAILED")
        return None

print("=" * 60)
print("UNIT_COP REGISTER FORMAT TEST")
print("=" * 60)
print()
print("According to table:")
print("  Unit_COP: add=389, modbus=40390, byte=1, data type=real")
print()
print("Current code reads: register 389 as 16-bit with 0.1 precision")
print()
print("=" * 60)
print()

# Example values (you'll see actual values from modbus)
print("Example test with typical COP values:")
print()

# Test case 1: COP = 3.5 as 16-bit
print("Test 1: If COP should be 3.5")
test_16bit_cop(35)  # 35 / 10 = 3.5
test_32bit_cop(0x4060, 0x0000)  # IEEE 754 for 3.5
print()

# Test case 2: COP = 4.2 as 16-bit
print("Test 2: If COP should be 4.2")
test_16bit_cop(42)  # 42 / 10 = 4.2
test_32bit_cop(0x4086, 0x6666)  # IEEE 754 for 4.2
print()

print("=" * 60)
print("CONCLUSION:")
print("Check your Home Assistant logs or modbus tool to see")
print("what values are actually in registers 389 and 390.")
print("If COP looks wrong, it might be using the wrong format.")
print("=" * 60)

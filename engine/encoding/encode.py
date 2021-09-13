import struct

ENCODERS = {}

def pack(fmt, *args):
	return encode(fmt, args)

def encode(fmt, data):
	if not fmt:
		if data:
			raise ValueError('Too much data')
		return b''
	return ENCODERS[fmt[0]](fmt, data)

def encode_unicode_string(fmt, data):
	subject = data[0]
	block = subject.encode('utf-16le')
	output = struct.pack('<I', 1 + len(block)//2) + block + b'\x00\x00'
	return output + encode(fmt[1:], data[1:])
ENCODERS['u'] = encode_unicode_string

def encode_array(fmt, data):
	array_elements = data[0]
	stack_depth = 0
	for index, element in enumerate(fmt):
		if element == '[':
			stack_depth += 1
		elif element == ']':
			stack_depth -= 1
		if stack_depth == 0:
			end_index = index
			break
	else:
		raise ValueError('Bad format; unbalanced brackets')
	remainder = encode(fmt[(end_index+1):], data[1:])
	this_fmt = fmt[1:end_index]
	return b''.join(encode(this_fmt, x) for x in array_elements) + remainder
ENCODERS['['] = encode_array

def struct_encoder_for(char):
	format_expr = "<{}".format(char)
	def st_encode(fmt, data):
		if not data:
			raise ValueError("Not enough data")
		return (struct.pack(format_expr, data[0]) +
				encode(fmt[1:], data[1:]))
	return st_encode

for base_format in 'bBiIhHlLqQfdx':
	ENCODERS[base_format] = struct_encoder_for(base_format)
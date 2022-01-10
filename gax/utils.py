import string
import utils
import time
import sys
import os


def xor_file(filename, key):
	if not os.path.isfile(filename):
		print(f'[!] Cannot find {filename}')
		return b''
	return xor(list(open(filename,'rb').read()), key)
	
def xor(raw_data, key):
	result = b''
	for i in range(len(raw_data)):
		result += bytes([raw_data[i] ^ key[i%len(key)]])
	return result

def hex2bytes(bstr):
	bs = []
	for element in bstr.split('x')[1:]:
		bs.append(ord(bytes.fromhex(element)))
	return bs

def key2int(k):
	return int.from_bytes(k,'big')


def int2key(N):
	return bytes(str(N),'ascii')

def recombine(cthexstr):
    ctl = []
    for i in list(range(0,len(cthexstr))):
        if i>0 and i%2==0:
            ctl.append(int(cthexstr[i-2:i],16))
    return ctl
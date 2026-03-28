import ctypes
import os

LIB_PATH = os.path.join(os.path.dirname(__file__), "libproject.so")
lib = ctypes.CDLL(LIB_PATH)

lib.valid_name.argtypes = [ctypes.c_char_p]
lib.valid_name.restype = ctypes.c_bool

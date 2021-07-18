import io
import re
import os
import sys
import time
import zlib
import base64
import marshal
from uncompyle6 import PYTHON_VERSION
from uncompyle6.main import decompile, decompile_file

ENCODEING = "utf-8"
ALGORITHOMS = (
    "base16",
    "base32",
    "base64",
    "base85",
    "marshal",
    "zlib",
    "pyc"
)


class CodeSearchAlgorithms:
    @staticmethod
    def bytecode(file_bytes: bytes) -> bytes:
        pattern: str = r"""(((b|bytes\()["'])(.+)(["']))"""
        string_data = re.findall(pattern, file_bytes.decode(ENCODEING))[0][3]
        return eval(f"b'{string_data}'")

    @staticmethod
    def base64_hash(file_bytes: bytes) -> str:
        pattern: str = r"""((?:(?:b|bytes\()?["'])([a-zA-Z0-9\=]+)(?:["']))"""
        return re.findall(pattern, file_bytes.decode(ENCODEING))[0][1]


class DecodingAlgorithms:
    def __init__(self, file_bytes: bytes, save_file: str):
        self.file_bytes = file_bytes
        print("Finding the best algorithm:")
        for algogithom in ALGORITHOMS:
            try:
                self.file_bytes = self.__getattribute__(algogithom)()
                print(f"# \033[1;32m{algogithom} ✓\033[0m", end="\r")
            except Exception:
                print(f"# \033[1;31m{algogithom}\033[0m")
                continue

            layers: int = 0
            while True:
                try:
                    self.file_bytes = self.__getattribute__(algogithom)()
                    layers += 1
                    print(f"# \033[1;32m{algogithom} layers {layers} ✓\033[0m", end="\r")
                    time.sleep(.02)
                except Exception:
                    print(f"\n# \033[1;32mDONE ✓\033[0m")
                    break
            break

        try:
            with open(save_file, "w") as file:
                file.write(self.file_bytes)
        except Exception:
            print("# \033[1;31mFailed to decode the file!\033[0m")

    def base16(self) -> str:
        return base64.b16decode(CodeSearchAlgorithms.base64_hash(self.file_bytes)).decode(ENCODEING)

    def base32(self) -> str:
        return base64.b32decode(CodeSearchAlgorithms.base64_hash(self.file_bytes)).decode(ENCODEING)

    def base64(self) -> str:
        return base64.b64decode(CodeSearchAlgorithms.base64_hash(self.file_bytes)).decode(ENCODEING)

    def base85(self) -> str:
        return base64.b85decode(CodeSearchAlgorithms.base64_hash(self.file_bytes)).decode(ENCODEING)

    def marshal(self) -> str:
        bytecode = marshal.loads(CodeSearchAlgorithms.bytecode(self.file_bytes))
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return out.getvalue() + '\n'

    def zlib(self) -> str:
        return zlib.decompress(CodeSearchAlgorithms.bytecode(self.file_bytes)).decode(ENCODEING)

    def pyc(self) -> str:
        with open(sys.argv[2], "w") as f:
            decompile_file(sys.argv[1], f)
        with open(sys.argv[2], "r") as f:
            data: str = f.read()
        if data == self.file_bytes:
            raise Exception()
        return data


if __name__ == '__main__':
    # sys.argv.append("/home/psh-team/Downloads/Telegram Desktop/MFB.pyc")
    # sys.argv.append("/home/psh-team/Downloads/Telegram Desktop/__pycache__/converM.cpython-38.pyc")
    # sys.argv.append("/home/psh-team/Downloads/Telegram Desktop/converM.py")
    # sys.argv.append("/home/psh-team/Downloads/Telegram Desktop/output.py")
    if len(sys.argv) > 2:
        if not os.path.isfile(sys.argv[1]):
            exit(f"# file not found!: {sys.argv[1]}")
        with open(sys.argv[1], "rb") as file:
            data: bytes = file.read()
        DecodingAlgorithms(data, sys.argv[2])
    else:
        print("USAGE:\n decode file.py output.py")

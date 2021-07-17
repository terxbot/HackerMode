import io
import re
import os
import sys
import time
import zlib
import marshal
from uncompyle6 import PYTHON_VERSION
from uncompyle6.main import decompile

ENCODEING = "utf-8"
ALGORITHOMS = (
    "marshal",
    "zlib",
)


class CodeSearchAlgorithms:
    @staticmethod
    def bytecode(string: str) -> bytes:
        pattern: str = r"""(((b|bytes\()["'])(.+)(["']))"""
        string_data = re.findall(pattern, string)[0][3]
        return eval(f"b'{string_data}'")

    @staticmethod
    def eval_filter(string: str) -> str:
        pattern: str = r"(eval(?:[\s]+)?\()"
        if len(eval_pos := re.findall(pattern, string)) < 0:
            return string

        eval_body: str = string[string.find(eval_pos[0]):string.find(eval_pos[0]) + len(eval_pos[0])]
        open_brackets: int = 1

        for _chr in string[string.find(eval_pos[0]) + len(eval_pos[0]):]:
            if _chr == "(":
                open_brackets += 1
            elif _chr == ")":
                open_brackets -= 1
            eval_body += _chr
            if open_brackets == 0:
                break
        return string.replace(eval_body, eval(eval_body[len(eval_pos[0]):-1]))


class DecodingAlgorithms:
    def __init__(self, string, save_file):
        self.string = string
        print("Finding the best algorithm:")
        for algogithom in ALGORITHOMS:
            try:
                self.string = self.__getattribute__(algogithom)()
                print(f"# \033[1;32m{algogithom} ✓\033[0m", end="\r")
            except Exception:
                print(f"# \033[1;31m{algogithom}\033[0m")
                continue

            layers: int = 0
            while True:
                try:
                    self.string = self.__getattribute__(algogithom)()
                    layers += 1
                    print(f"# \033[1;32m{algogithom} layers {layers} ✓\033[0m", end="\r")
                    time.sleep(.02)
                except Exception:
                    print(f"\n# \033[1;32mDONE ✓\033[0m")
                    break
            break

        with open(save_file, "w") as file:
            file.write(self.string)

    def marshal(self) -> str:
        bytecode = marshal.loads(CodeSearchAlgorithms.bytecode(self.string))
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return out.getvalue() + '\n'

    def zlib(self) -> str:
        return zlib.decompress(CodeSearchAlgorithms.bytecode(self.string)).decode(encoding=ENCODEING)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        if not os.path.isfile(sys.argv[1]):
            exit(f"# file not found!: {sys.argv[1]}")
        with open(sys.argv[1], "r") as file:
            data = file.read()
        DecodingAlgorithms(data, sys.argv[2])
    else:
        print("USAGE:\n decode file.py output.py")

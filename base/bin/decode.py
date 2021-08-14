#!/usr/bin/python3
import io
import re
import os
import sys
import dis
import time
import zlib
import base64
import marshal
from pkgutil import read_code

from uncompyle6 import PYTHON_VERSION
from uncompyle6.main import decompile

sys.path.append(__file__.rsplit("/", 2)[0])

CONFIG = __import__("config").Config
ENCODEING = "utf-8"
OLD_EXEC = exec
OLD_EVAL = eval
ALGORITHOMS = (
    "zlib",
    "marshal",
    "base16",
    "base32",
    "base64",
    "base85",
    "exec-function",
    "machine-code",
    "eval-filter",
    "string-filter",
)
COPYRIGHT = """
# Decoded by HackerMode tool...
# Copyright: PSH-TEAM
# Follow us on telegram ( @psh_team )
""".lstrip()


class CodeSearchAlgorithms:
    @staticmethod
    def bytecode(string: str) -> bytes:
        pattern: str = r"""(((b|bytes\()["'])(.+)(["']))"""
        length: int = 0
        string_data: str = ""
        for string in re.findall(pattern, string):
            if len(string[3]) > length:
                length = len(string[3])
                string_data = string[3]
        if not string_data:
            raise Exception()
        return eval(f"b'{string_data}'")

    @staticmethod
    def function(string: str, function_name):
        pattern: str = r"(" + function_name + r"(?:[\s]+)?\()"
        if len(eval_poss := re.findall(pattern, string)) < 0:
            raise Exception()
        for eval_pos in eval_poss:
            eval_function: str = string[string.find(eval_pos):string.find(eval_pos) + len(eval_pos)]
            open_brackets: int = 1

            for _chr in string[string.find(eval_pos) + len(eval_pos):]:
                if _chr == "(":
                    open_brackets += 1
                elif _chr == ")":
                    open_brackets -= 1
                eval_function += _chr
                if open_brackets == 0:
                    break
            string = string[string.find(eval_function) + len(eval_function):]
            yield eval_function

    @staticmethod
    def string_filter(string: str):
        pattern = r"""(["'](?:\\[\w0-9]+)+["'])"""
        if len(strings := re.findall(pattern, string)) < 0:
            raise Exception()
        for _str in strings:
            yield _str


class DecodingAlgorithms:
    def __init__(self, file_data, save_file):
        self.file_data = file_data
        self._custom_exec_data = None
        self._custom_compile_data = None
        self._custom_eval_data = None

        if CONFIG.get('actions', 'DEBUG', cast=bool, default=False):
            sys.__dict__['EXIT'.lower()]()

        print("Finding the best algorithm:")
        for algogithom in ALGORITHOMS:
            try:
                self.file_data = self.__getattribute__(algogithom.replace("-", "_"))()
                print(f"# \033[1;32m{algogithom} ✓\033[0m", end="\r")
            except Exception:
                print(f"# \033[1;31m{algogithom}\033[0m")
                continue

            if "filter" in algogithom:
                print("")
                continue

            layers: int = 0
            while True:
                try:
                    self.file_data = self.__getattribute__(algogithom)()
                    layers += 1
                    print(f"# \033[1;32m{algogithom} layers {layers} ✓\033[0m", end="\r")
                    time.sleep(.02)
                    if not self.file_data.strip():
                        raise Exception()
                except Exception:
                    print(f"\n# \033[1;32mDONE ✓\033[0m")
                    break
            break
        try:
            with open(save_file, "w") as file:
                if not COPYRIGHT in self.file_data:
                    file.write(COPYRIGHT + self.file_data)
                else:
                    file.write(self.file_data)
        except Exception as e:
            print("# \033[1;31mFailed to decode the file!\033[0m")

    def marshal(self) -> str:
        bytecode = marshal.loads(CodeSearchAlgorithms.bytecode(self.file_data))
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return "\n".join(out.getvalue().split("\n")[4:]) + '\n'

    def zlib(self) -> str:
        return zlib.decompress(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base16(self) -> str:
        return base64.b16decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base32(self) -> str:
        return base64.b32decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base64(self) -> str:
        return base64.b64decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base85(self) -> str:
        return base64.b85decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def exec_function(self) -> str:
        self._custom_exec_data = None
        self._custom_compile_data = None
        self._custom_eval_data = None

        def exec(*args):
            self._custom_exec_data = args[0]

        def compile(*args):
            self._custom_compile_data = args[0]

        def eval(*args):
            self._custom_eval_data = args[0]

        OLD_EXEC(self.file_data)
        if type(self._custom_exec_data) is str:
            return self._custom_exec_data
        elif self._custom_compile_data != None:
            if type(self._custom_compile_data) == bytes:
                return self._custom_compile_data.decode(ENCODEING)
            elif type(self._custom_compile_data) == str:
                return self._custom_compile_data
        elif type(self._custom_eval_data) is str:
            return self._custom_exec_data

        if self._custom_exec_data:
            bytecode = self._custom_exec_data
        elif self._custom_compile_data:
            bytecode = self._custom_compile_data
        else:
            bytecode = self._custom_eval_data

        try:
            out = io.StringIO()
            version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
            decompile(version, bytecode, out, showast=False)
            return "\n".join(out.getvalue().split("\n")[4:]) + '\n'
        except Exception:
            output: str = ""
            for arg in dir(bytecode):
                if arg.startswith("co_"):
                    out = bytecode.__getattribute__(arg)
                    if not (type(out) in (tuple, list, set, dict)):
                        if type(out) is str:
                            output += f"\n{arg.replace('co_', '').upper()}: '{out}'"
                        else:
                            output += f"\n{arg.replace('co_', '').upper()}: {out}"
            for arg in dir(bytecode):
                if arg.startswith("co_"):
                    out = bytecode.__getattribute__(arg)
                    if type(out) in (tuple, list, set, dict):
                        if out:
                            output += f"\n\n{arg.replace('co_', '').upper()}:"
                            for o in out:
                                if type(o) is str:
                                    output += (f"\n  {bytes(o,ENCODEING)}").replace(" b'"," '")
                                else:
                                    output += f"\n  {o}"
            return output

    def machine_code(self) -> str:
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, self.file_data, out, showast=False)
        data = out.getvalue() + '\n'
        if self.file_data == data:
            raise Exception()
        return data

    def eval_filter(self) -> str:
        def root_search(all_eval_functions):
            for func in all_eval_functions:
                if not func.strip():
                    all_eval_functions.remove(func)

            exceptions = 0
            for eval_f in all_eval_functions:
                try:
                    eval_body = re.findall(r"\((.+)\)", eval_f)[0]
                    bad_functions = ["eval", "exec"]
                    is_in = False
                    for function in bad_functions:
                        if function in eval_body:
                            is_in = True
                    if is_in:
                        root_search(list(set(list(CodeSearchAlgorithms.function(eval_body, "eval")))))
                        exceptions += 1
                        continue
                except IndexError:
                    continue

                try:
                    try:
                        eval_data = eval(f"b{eval_body}").decode(ENCODEING)
                    except Exception:
                        eval_data = eval(eval_body)
                    self.file_data = self.file_data.replace(eval_f, eval_data)
                except Exception:
                    exceptions += 1
            if exceptions == len(all_eval_functions):
                raise Exception(
                    f"Exception: exceptions:{exceptions} == len(all_eval_functions):{len(all_eval_functions)}")

        root_search(list(set(list(CodeSearchAlgorithms.function(self.file_data, "eval")))))
        return self.file_data

    def string_filter(self) -> str:
        all_strings = list(set(list(CodeSearchAlgorithms.string_filter(self.file_data))))
        exceptions = 0
        for _str in all_strings:
            try:
                self.file_data = self.file_data.replace(_str, f"'{eval(_str)}'")
            except Exception:
                exceptions += 1
        if exceptions == len(all_strings):
            raise Exception()
        return self.file_data


if __name__ == '__main__':
    if len(sys.argv) > 2:
        if not os.path.isfile(sys.argv[1]):
            exit(f"# file not found!: {sys.argv[1]}")
        try:
            with open(sys.argv[1], "r") as file:
                data = file.read()
        except UnicodeDecodeError:
            with io.open_code(sys.argv[1]) as f:
                data = read_code(f)
        DecodingAlgorithms(data, sys.argv[2])
    else:
        print("USAGE:\n decode file.py output.py")

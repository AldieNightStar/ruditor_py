import asyncio
import sys

from ruditor_py.texter import parse_text

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Please, provide [input.txt] and [output.txt] file")
        print("")
        print("[!] Make sure you have running LM Studio at: http://127.0.0.1:1234/v1")
        print("")
        return
    asyncio.run(parse_text("text.txt", "text2.txt"))
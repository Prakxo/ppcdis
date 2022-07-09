"""
Diffs the sections and relocations (where possible) of a dol/rel file
"""

from argparse import ArgumentParser
import colorama as col

from binarybase import BinaryReader
from binaryrel import RelReader, RelSize
from binaryyml import load_binary_yml

col.init()

def print_diff(name: str, a: int, b: int):
    """Prints the diff of two integer values"""
    
    if a == b:
        clr = ""
    elif b > a:
        clr = col.Fore.LIGHTBLUE_EX
    else:
        clr = col.Fore.RED

    print(f"\t{name:10}:  {a:#10x}  {clr}{b:#10x}{col.Style.RESET_ALL}")

def print_eq(name: str, a, b):
    """Prints the equality of two objects"""

    if a == b:
        msg = "yes"
    else:
        msg = col.Fore.RED + "no"
    
    print(f"\t{name:10}:  {msg}{col.Style.RESET_ALL}")

def diff_secs(good: BinaryReader, test: BinaryReader) -> bool:
    """Prints the diff of the sections in two binaries
    Returns whether any diffs were found"""
    
    any_diff = False

    for i, (s1, s2) in enumerate(zip(good.sections, test.sections)):
        hash1 = good.section_sha(s1)
        hash2 = test.section_sha(s2)
        if (
            hash1 != hash2 or
            s1.size != s2.size
        ):
            any_diff = True
            print(f"Section {i} {s1.name}")
            print_diff("Offset", s1.offset, s2.offset)
            print_diff("Address", s1.addr, s2.addr)
            print_diff("Size", s1.size, s2.size)
            print_eq("Contents", hash1, hash2)

    return any_diff

def diff_relocs(good: RelReader, test: RelReader):
    """Prints the diff of the relocations in two rels"""

    for i, (r1, r2) in enumerate(zip(good.relocs, test.relocs)):
        if r1 != r2:
            print(f"Reloc {i} (0x{i * RelSize.RELOC_ENTRY})")

            print_diff("Module", r1.target_module, r2.target_module)
            print_diff("Offset", r1.offset, r2.offset)
            print_diff("Type", r1.t, r2.t)
            print_diff("Section", r1.section, r2.section)
            print_diff("Addend", r1.addend, r2.addend)
            print_diff(
                "Target",
                good.sec_offs_to_addr(r1.section, r1.addend),
                test.sec_offs_to_addr(r2.section, r2.addend)
            )
            print_diff("Write Addr", r1.write_addr, r2.write_addr)

if __name__=="__main__":
    hex_int = lambda s: int(s, 16)
    parser = ArgumentParser()
    parser.add_argument("good", type=str, help="Path to good binary yml")
    parser.add_argument("test", type=str, help="Path to test binary")
    args = parser.parse_args()

    # Load binaries
    good = load_binary_yml(args.good)
    test = good.load_other(args.test)

    # Do diff
    ret = diff_secs(good, test)
    if not ret and isinstance(good, RelReader):
        diff_relocs(good, test)

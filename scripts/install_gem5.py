import os
import subprocess
import sys

from contextlib import chdir
from pathlib import Path


help_options = ["help", "-h", "--help"]

isa_options = ["ARM", "MIPS", "POWER", "RISCV", "SPARC", "X86"]

variant_options = [
    "debug",
    "opt",
    "fast",
]

help = f"""Usage:
    python3 {sys.argv[0]} ISA VARIANT
    python3 {sys.argv[0]} {{help|-h|--help}}

Configure and build gem5 for selected ISA with VARIANT optimization configuration.
You can read more about the gem5 build at https://www.gem5.org/documentation/general_docs/building.

ISA available values:
{"\n".join([f"    - {isa}" for isa in isa_options])}

VARIANT available values:
{"\n".join([f"    - {var}" for var in variant_options])}

Examples:
    python3 {sys.argv[0]} X86 opt
        Build gem5 for X86 isa with .opt gem5 configuration.
    python3 {sys.argv[0]} help
        Print this help message.

"""

base_dir = Path(__file__).parent
root_dir = base_dir.parent
configs_dir = root_dir.joinpath("configs")
gem5_dir = root_dir.joinpath("thirdparty", "gem5")
m5ops_dir = gem5_dir.joinpath("util", "m5")
gem5_build_cache_dir = gem5_dir.joinpath("build_cache")


def parse_args(args: list[str]) -> tuple[str, str]:
    if len(sys.argv) == 2 and sys.argv[1] in help_options:
        print(help)
        sys.exit(0)
    if len(sys.argv) != 3:
        print("Illegal number of arguments")
        print(help)
        sys.exit(1)
    isa_opt = sys.argv[1].upper()
    if isa_opt not in isa_options:
        print("Illegal ISA value: ")
        print(help)
        sys.exit(1)
    variant_opt = sys.argv[2].lower()
    if variant_opt not in variant_options:
        print("Illegal VARIANT value")
        print(help)
        sys.exit(1)
    return isa_opt, variant_opt


def build_gem5(isa: str, var: str) -> None:
    nproc = os.cpu_count()
    os.chdir(gem5_dir)
    subprocess.run(["scons", "defconfig", f"build/{isa}" f"build_opts/{isa}"])
    subprocess.run(["scons", "setconfig", f"build/{isa}", f"M5_BUILD_CACHE={gem5_build_cache_dir}"])
    subprocess.run(["scons", f"build/{isa}/gem5.{var}", "-j", f"{nproc}"])
    # Build M5 ops
    os.chdir(m5ops_dir)
    m5_isa = isa.lower()
    subprocess.run(["scons", f"build/{m5_isa}/out/m5", "-j", f"{nproc}"])


if __name__ == "__main__":
    isa, var = parse_args(sys.argv)
    build_gem5(isa, var)

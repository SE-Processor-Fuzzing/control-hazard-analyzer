import os
import subprocess
import sys

from pathlib import Path


help_options = ["help", "-h", "--help"]

isa_options = ["ARM", "MIPS", "POWER", "RISCV", "SPARC", "X86"]

variant_options = [
    "debug",
    "opt",
    "fast",
]

help = f"""Usage:
    python3 {sys.argv[0]} ISA VARIANT CACHE_PATH
    python3 {sys.argv[0]} {{help|-h|--help}}

Configure and build gem5 for selected ISA with VARIANT optimization configuration and save build cache to CACHE_PATH.
You can read more about the gem5 build at https://www.gem5.org/documentation/general_docs/building.

ISA available values:
{"\n".join([f"    - {isa}" for isa in isa_options])}

VARIANT available values:
{"\n".join([f"    - {var}" for var in variant_options])}

Examples:
    python3 {sys.argv[0]} X86 opt ./gem5_build_cache
        Build gem5 for X86 isa with .opt gem5 configuration
        and save build cache to ./gem5_build_cache directory.
    python3 {sys.argv[0]} help
        Print this help message.

"""

base_dir = Path(__file__).parent
root_dir = base_dir.parent
configs_dir = root_dir.joinpath("configs")
gem5_dir = root_dir.joinpath("thirdparty", "gem5")
m5ops_dir = gem5_dir.joinpath("util", "m5")


def parse_args(args: list[str]) -> tuple[str, str, Path]:
    if len(args) == 2 and args[1] in help_options:
        print(help)
        sys.exit(0)
    if len(args) != 4:
        print("Illegal number of arguments")
        print(help)
        sys.exit(1)
    isa_opt = args[1].upper()
    if isa_opt not in isa_options:
        print("Illegal ISA value: ")
        print(help)
        sys.exit(1)
    variant_opt = args[2].lower()
    if variant_opt not in variant_options:
        print("Illegal VARIANT value")
        print(help)
        sys.exit(1)
    cache_path_opt = Path(args[3])
    return isa_opt, variant_opt, cache_path_opt


def build_gem5(isa: str, var: str, cache_path: Path) -> None:
    nproc = os.cpu_count()
    # Build gem5 with cache
    subprocess.run(["scons", "defconfig", f"build/{isa}", f"build_opts/{isa}", "--install-hooks"], cwd=gem5_dir)
    subprocess.run(["scons", "setconfig", f"build/{isa}", f"M5_BUILD_CACHE={cache_path}"], cwd=gem5_dir)
    subprocess.run(["scons", f"build/{isa}/gem5.{var}", "-j", f"{nproc}"], cwd=gem5_dir)
    # Build M5 ops
    m5_isa = isa.lower()
    subprocess.run(["scons", f"./build/{m5_isa}/out/m5", "-j", f"{nproc}"], cwd=m5ops_dir)


if __name__ == "__main__":
    isa, var, cache_path = parse_args(sys.argv)
    build_gem5(isa, var, cache_path)

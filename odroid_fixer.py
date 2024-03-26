import json
from pathlib import Path
import sys

KEY_BRANCH = "branchPred.lookups"
KEY_PREDICTED_BRANCH = "branchPred.condCorrect"


if len(sys.argv) < 3:
    print("Bububububbubu")
    exit()

src_dir = Path(sys.argv[1])
out_dir = Path(sys.argv[2])

for f in src_dir.iterdir():
    nm = f.name
    with open(out_dir.joinpath(nm), "rt+") as writter:
        with open(f, "rt") as reader:
            print(nm)
            src = reader.read()
            out = writter.read()
            src_dict = json.loads(src)
            out_dict = json.loads(out)
            out_dict[KEY_PREDICTED_BRANCH] += src_dict[KEY_BRANCH] - out_dict[KEY_BRANCH]
            out_dict[KEY_BRANCH] = src_dict[KEY_BRANCH]
            writter.seek(0, 0)
            writter.write(json.dumps(out_dict))

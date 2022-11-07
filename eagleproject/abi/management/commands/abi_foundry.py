"""
Import ABIs from Foundry deployment file(s) into this app's data

Usage
-----

    python manage.py abi_foundry /path/to/ousd-governance/build/deployments/1/*.json

"""
import json
from pathlib import Path
from typing import Any, Dict, List

from django.core.management.base import BaseCommand

from abi import ABI_DIR


def process_files(files: List[Path], overwrite=False, skip_conflict=False):
    print(f"Processing {len(files)} deployment files...")

    for fil in files:
        if not fil.is_file():
            raise Exception(f"{fil} does not appear to be a file")

        raw_text = fil.read_text("utf-8", "strict")
        json_obj = json.loads(raw_text)

        if "abi" not in json_obj:
            print(f"{fil} does not have an ABI prop, skipping.")
            continue

        abi = json_obj["abi"]
        name = json_obj["contractName"]
        outfile = ABI_DIR.joinpath(f"{name}.abi.json")

        if outfile.exists():
            if skip_conflict:
                print(f"{outfile} exists, skipping...")
                continue
            elif not overwrite:
                raise Exception(
                    f"{outfile} exists and overwriting is disabled."
                )

        print(f"Writing ABI to {outfile}")

        # outfile.write_text(json.dumps(abi), encoding="utf-8")


class Command(BaseCommand):
    help = "Generate ABI files from Hardhat deployment files"

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+", type=Path)

        # Named (optional) arguments
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite files if they exist",
        )
        parser.add_argument(
            "--skip-conflict",
            action="store_true",
            help="Skip files if they exist",
        )

    def handle(self, *args, **options):
        process_files(
            options["files"], options["overwrite"], options["skip_conflict"]
        )

from __future__ import annotations
from urllib.request import urlopen
from functools import partial
import re
import json
import argparse
from datetime import datetime, timezone
import datetime as dt
from itertools import zip_longest
from operator import itemgetter
from packaging.version import parse as parse_version, Version, LegacyVersion
from packaging.requirements import Requirement
from typing import Dict, Tuple, cast, List, Union, TYPE_CHECKING, Optional
from concurrent.futures import ThreadPoolExecutor


if TYPE_CHECKING:

    from typing import Protocol

    class Arguments(Protocol):
        date: dt.date
        requirements: List[Requirement]


ParsedVersion = Union[Version, LegacyVersion]


def fetch_releases(project: str) -> Dict[ParsedVersion, list]:
    pypi_endpoint = f"https://pypi.org/pypi/{project}/json"
    with urlopen(pypi_endpoint) as response:
        releases: Dict[str, list] = json.loads(response.read().decode()).get(
            "releases"
        )
    return {
        parse_version(version): files for version, files in releases.items()
    }


def parse_date(date_str: str) -> dt.date:
    # this if only checks that after str.split("-") there is a maximum of
    # 3 items, so that the following cast is correct
    # the map(int, ...) guarantees that the substrings are integers
    # the validity of the integers themselves is checked by dt.date
    if not re.match(r"^[^-]*(-[^-]*){0,2}$", date_str):
        raise ValueError("Invalid string format")

    date_args = cast(
        Tuple[int, int, int],
        [
            selected or default
            for selected, default in zip_longest(
                map(int, date_str.split("-")), [1, 1, 1], fillvalue=None
            )
        ],
    )
    return dt.date(*date_args)


def get_latest_version(
    date: dt.date, releases: Dict[ParsedVersion, list]
) -> ParsedVersion:
    # releases with all files uploaded before target date
    all_valid = [
        version
        for version, files in releases.items()
        if files  # apparently, some releases don't have files
        and all(
            dt.date.fromisoformat(file["upload_time_iso_8601"].split("T")[0])
            < date
            for file in files
        )
    ]
    *_, latest = sorted(all_valid)
    return latest


def process_requirement(
    date: dt.date, requirement: Requirement
) -> Requirement:
    # add specifier only if the req doesn't have one
    if not requirement.specifier:
        releases = fetch_releases(requirement.name)
        latest_version = get_latest_version(date, releases)
        requirement.specifier &= f"<={latest_version}"
    return requirement


def parse_args(args: Optional[List[str]] = None) -> Arguments:
    parser = argparse.ArgumentParser(
        description="Fetch latest version of pypi packages at a given date"
    )
    parser.add_argument("date", type=parse_date)
    parser.add_argument(
        "requirements", metavar="pkg", nargs="+", type=Requirement
    )

    return parser.parse_args(args)


def main() -> None:
    #    for requirement in args.requirements:
    #       print(process_requirement(args.date, requirement))
    args: Arguments = parse_args()
    with ThreadPoolExecutor(max_workers=10) as e:
        for requirement in e.map(
            partial(process_requirement, args.date), args.requirements
        ):
            print(requirement)


if __name__ == "__main__":
    main()

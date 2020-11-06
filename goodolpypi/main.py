from urllib.request import urlopen
from functools import partial
import re
import json
import argparse
from datetime import datetime, timezone
from itertools import zip_longest
from operator import itemgetter
from packaging.version import parse as parse_version, Version, LegacyVersion
from packaging.requirements import Requirement
from typing import Dict, Tuple, cast, List, Union, Protocol
from concurrent.futures import ThreadPoolExecutor

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


def parse_date(date_str: str) -> datetime:
    assert re.match(r"^\d{4}(-\d{2}){0,2}", date_str), "Invalid string format"

    dt_args = cast(
        Tuple[int, int, int],
        [
            selected or default
            for selected, default in zip_longest(
                map(int, date_str.split("-")), [1, 1, 1], fillvalue=None
            )
        ],
    )
    return datetime(
        *dt_args,
        tzinfo=timezone.utc,
    )


def fetch_latest_version(
    date: datetime, requirement: Requirement
) -> ParsedVersion:
    releases = fetch_releases(requirement.name)
    # releases with all files uploaded before target date
    all_valid = [
        version
        for version, files in releases.items()
        if files  # apparently, some releases don't have files
        and all(
            datetime.fromisoformat(
                file["upload_time_iso_8601"].replace("Z", "+00:00")
            )
            < date
            for file in files
        )
    ]
    *_, latest = sorted(all_valid)
    return latest


def process_requirement(
    date: datetime, requirement: Requirement
) -> Requirement:
    # add specifier only if the req doesn't have one
    if not requirement.specifier:
        latest_version = fetch_latest_version(date, requirement)
        requirement.specifier &= f"<={latest_version}"
    return requirement


class Arguments(Protocol):
    date: datetime
    requirements: List[Requirement]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch latest version of pypi packages at a given date"
    )
    parser.add_argument("date", type=parse_date)
    parser.add_argument(
        "requirements", metavar="pkg", nargs="+", type=Requirement
    )

    args: Arguments = parser.parse_args()

    #    for requirement in args.requirements:
    #       print(process_requirement(args.date, requirement))
    with ThreadPoolExecutor(max_workers=10) as e:
        for requirement in e.map(
            partial(process_requirement, args.date), args.requirements
        ):
            print(requirement)


if __name__ == "__main__":
    main()

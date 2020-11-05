from urllib.request import urlopen
import json
import argparse
from datetime import datetime, timezone
from itertools import zip_longest
from operator import itemgetter
from packaging import version


def fetch_releases(project):
    pypi_endpoint = f"https://pypi.org/pypi/{project}/json"
    response = urlopen(pypi_endpoint)
    releases = json.loads(response.read().decode()).get("releases")
    return releases


def parse_date(date_str):
    # defaults for year, month, day
    return datetime(
        *[
            selected or default
            for selected, default in zip_longest(
                map(int, date_str.split("-")), [1, 1, 1], fillvalue=None
            )
        ],
        tzinfo=timezone.utc,
    )


def fetch_latest_version(date, project):
    releases = fetch_releases(project)
    # releases with all files uploaded before target date
    all_valid = [
        version
        for version, files in releases.items()
        if files
        and all(
            datetime.fromisoformat(
                file["upload_time_iso_8601"].replace("Z", "+00:00")
            )
            < date
            for file in files
        )
    ]
    *_, latest = sorted(all_valid, key=version.parse)
    return latest


def main():
    parser = argparse.ArgumentParser(
        description="Fetch latest version of pypi packages at a given date"
    )
    parser.add_argument("date", type=parse_date)
    parser.add_argument("packages", metavar="package", nargs="+")
    args = parser.parse_args()
    for package in args.packages:
        print(fetch_latest_version(args.date, package))


if __name__ == "__main__":
    main()

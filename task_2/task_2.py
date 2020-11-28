from functools import total_ordering
from itertools import zip_longest


@total_ordering
class Version:
    def __init__(self, version: str):
        self.version = version
        if '-' in version:
            self.components, self.prerelease = version.split('-')
        else:
            self.components, self.prerelease = version, None

        self.components = self.components.replace('b', '.1')

    def __eq__(self, other):
        return self.version == other.version

    def __lt__(self, other):
        for self_c, other_c in zip_longest(self.components.split('.'), other.components.split('.'), fillvalue=0):
            if self_c != other_c:
                return int(self_c) < int(other_c)
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease
        else:
            return bool(self.prerelease)


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),

        ("1.2.2.0", "1.2.2.1"),
        ("1.2.2.3.4", "1.2.2.3.4.5"),

    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
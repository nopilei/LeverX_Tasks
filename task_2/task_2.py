import re
from functools import total_ordering
from collections import namedtuple


@total_ordering
class Version:
    _REGEX = re.compile('^(?P<major>0|[1-9]\d*[a-z]?)\.'
                        '(?P<minor>0|[1-9]\d*[a-z]?)\.'
                        '(?P<patch>0|[1-9]\d*[a-z]?)'
                        '(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
                        '(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
                        '(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')

    # Container for storing necessary info from version string
    _MainComponents = namedtuple('Triple', ['major', 'minor', 'patch', 'prerelease'])

    def __init__(self, version: str):
        if re.fullmatch(self._REGEX, version) is None:
            raise ValueError('Version string does not match the pattern.')

        if '+' in version:
            version = version[:version.find('+')]  # Drop metadata
        major, minor, left = version.split('.', maxsplit=2)
        if '-' not in left:
            patch, prerelease = left, None
        else:
            patch, prerelease = left.split('-')
        self.components = self._MainComponents(major, minor, patch, prerelease)

    def __eq__(self, other):
        return self.components == other.components

    def __lt__(self, other):
        #  First, compare majors, minors and patches
        for self_component, other_component in zip(self.components[:-1], other.components[:-1]):
            if self_component != other_component:
                #  Start from comparing components as numbers if they are
                if (self_component + other_component).isdigit():
                    return int(self_component) < int(other_component)
                else:
                    #  Else, if one of them have letter at the end, do the following
                    self_component, self_last_char = self_component[:-1], self_component[-1]
                    other_component, other_last_char = other_component[:-1], other_component[-1]
                    if self_component != other_component:
                        return int(self_component) < int(other_component)
                    else:
                        return self_last_char > other_last_char

        #  If majors, minors and patches are equal, compare prereleases
        self_prerelease, other_prerelease = self.components.prerelease, other.components.prerelease
        if self_prerelease and other_prerelease:
            self_parts, other_parts = self_prerelease.split('.'), other_prerelease.split('.')
            for s_part, o_part in zip(self_parts, other_parts):
                if s_part != o_part:
                    if (s_part + o_part).isdigit():
                        return int(s_part) < int(o_part)
                    else:
                        return s_part < o_part
                elif s_part == self_parts[-1] or o_part == other_parts[-1]:
                    return len(self_parts) < len(other_parts)
        else:
            return bool(self_prerelease)


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),

        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta"),
        ("1.0.0-alpha.beta", "1.0.0-beta"),
        ("1.0.0-beta", "1.0.0-beta.2"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-beta.11", "1.0.0-rc.1"),
        ("1.0.0-rc.1", "1.0.0"),
        ("1.4.1", "1.323.0"),
        ("1.4.1", "1.323.0+asdawd"),
    ]
    #

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
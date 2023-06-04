"""Utility functions."""

import contextlib
import hashlib
import re
import time
import urllib
from collections.abc import Collection, Generator, Iterable
from decimal import ROUND_HALF_UP, Decimal
from itertools import islice
from typing import cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from defusedxml import ElementTree

from .exceptions import XMLRootElementError
from .type import URL, Namespaces, Response


async def parse_source_response_xml(response: Response, allowed_root_tags: Collection[str] | None = None) -> Element:
    """Parse the XML from the source response."""
    tree = cast(Element, ElementTree.fromstring(await response.text(), forbid_dtd=False))
    if allowed_root_tags and tree.tag not in allowed_root_tags:
        raise XMLRootElementError(allowed_root_tags, tree.tag)
    return tree


async def parse_source_response_xml_with_namespace(
    response: Response,
    allowed_root_tags: Collection[str] | None = None,
) -> tuple[Element, Namespaces]:
    """Parse the XML with namespace from the source response."""
    tree = await parse_source_response_xml(response, allowed_root_tags)
    # ElementTree has no API to get the namespace so we extract it from the root tag:
    namespaces = {"ns": tree.tag.split("}")[0][1:]}
    return tree, namespaces


Substitution = tuple[re.Pattern[str], str]
MEMORY_ADDRESS_SUB: Substitution = (re.compile(r" at 0x[0-9abcdef]+>"), ">")
TOKEN_SUB: Substitution = (re.compile(r"token=[^&]+"), "token=<redacted>")
KEY_SUB: Substitution = (re.compile(r"key=[0-9abcdef]+"), "key=<redacted>")
HASH_SUB: Substitution = (re.compile(r"(?i)[a-f0-9]{20,}"), "hashremoved")


def stable_traceback(traceback: str) -> str:
    """Remove memory addresses from the traceback so make it easier to compare tracebacks."""
    for reg_exp, replacement in [MEMORY_ADDRESS_SUB, TOKEN_SUB, KEY_SUB]:
        traceback = re.sub(reg_exp, replacement, traceback)
    return traceback


def tokenless(url: str) -> str:
    """Strip private tokens from (text with) urls."""
    return re.sub(TOKEN_SUB[0], TOKEN_SUB[1], url)


def hashless(url: URL) -> URL:
    """Strip hashes from the url so that it can be used as part of a issue key."""
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(str(url))
    path = re.sub(HASH_SUB[0], HASH_SUB[1], path)
    query = re.sub(HASH_SUB[0], HASH_SUB[1], query)
    fragment = re.sub(HASH_SUB[0], HASH_SUB[1], fragment)
    return URL(urllib.parse.urlunsplit((scheme, netloc, path, query, fragment)))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    md5 = hashlib.md5(string.encode("utf-8"), usedforsecurity=False)  # noqa: DUO130,RUF100
    return md5.hexdigest()


def sha1_hash(string: str) -> str:
    """Return a sha1 hash of the string."""
    sha1 = hashlib.sha1(string.encode("utf-8"), usedforsecurity=False)  # noqa: DUO130,RUF100
    return sha1.hexdigest()


def is_regexp(string: str) -> bool:
    """Return whether the string looks like a regular expression."""
    return bool(set("$^?.+*[]") & set(string))


def match_string_or_regular_expression(string: str, strings_and_or_regular_expressions: Collection[str]) -> bool:
    """Return whether the string is equal to one of the strings or matches one of the regular expressions."""
    for string_or_regular_expression in strings_and_or_regular_expressions:
        if is_regexp(string_or_regular_expression):
            if re.match(string_or_regular_expression, string):
                return True
        elif string_or_regular_expression == string:
            return True
    return False


def iterable_to_batches(iterable: Iterable, batch_size: int) -> Iterable:
    """Produce batches of iterables, from a given iterable."""
    iterable = iter(iterable)
    return iter(lambda: tuple(islice(iterable, batch_size)), ())


def decimal_round_half_up(dec: Decimal | float) -> int:
    """Round decimal or float to nearest integer, with ties going away from zero."""
    return int(Decimal(dec).to_integral_value(ROUND_HALF_UP))


class Clock:
    """Class to keep track of time."""

    def __init__(self) -> None:
        self.start = time.perf_counter()
        self.duration = 0.0

    def stop(self) -> None:
        """Stop the clock."""
        self.duration = time.perf_counter() - self.start


@contextlib.contextmanager
def timer() -> Generator[Clock, None, None]:
    """Timer context manager."""
    clock = Clock()
    yield clock
    clock.stop()

#!/usr/bin/env python3
"""Unsent: The Micro-Confession Sprint -- make.fun entry.

A two-part micro-confession: a "To:" line naming who it was meant
for, and the unsent message itself, one line of at most 200
characters, written exactly as it was typed. The confession is kept
in entry.txt next to this file; this program reads those exact
bytes, checks them against the bounty gate rule by rule, and
publishes them byte for byte to /output/entry.txt.

The entry: "To: my best friend from school" / "I never told you I
was the one who told everyone about your crush in year nine, and
every time you say I'm the only person you trust, I feel sick."
It wins on the judge's criteria because it is a real confession,
not a joke: the writer betrayed the one person who trusts them
completely, and the reason it stayed in drafts is felt in the
words -- "every time you say I'm the only person you trust, I
feel sick" -- rather than stated. Sending it would detonate the
friendship, so it could never be sent, and it is too afraid and
too guilty to send. The To: line and the message need each other:
the betrayal was against this exact friend, and "the only person
you trust" only lands addressed to them; swapping the addressee
would break it. Candidates I considered and cut: a grief entry to
a sister about their late father's last voicemail (aching and
specific, but its core is grief about Dad, not a confession to the
addressee), and a school-crush entry about rehearsing a confession
for three years (too late, but gentler nostalgia -- less ache,
less reason it could never be sent). The betrayal won because the
unsent-ness is intrinsic to the message itself: it is the one
thing the writer can never tell the one person who trusts them.

Gate (from the kit's RULES.txt): /output/entry.txt must be UTF-8
text of 1 to 260 characters, not only white space. This program
models the gate as a small object with one method per rule, so a
failure names the rule that refused the entry, and it also guards
the two silent corruptions that would waste the entry: trailing
white space that a careless write would add, and control
characters that would make the line unreadable. It additionally
checks the entry's two-part shape: exactly one "To:" line and
exactly one message line of at most 200 characters.

Run it the way the grader does:

    python3 main.py
"""

import os
import sys

ENTRY_FILE = "entry.txt"
OUT_PATH = "/output/entry.txt"


class Gate:
    """The bounty gate, one method per rule, limits in one place."""

    def __init__(self, min_chars=1, max_chars=260, max_msg_chars=200):
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.max_msg_chars = max_msg_chars

    def rules(self, text):
        """Yield (rule, passed, detail) for every gate rule."""
        yield ("utf-8", True, "decoded as UTF-8")
        yield ("length", self.min_chars <= len(text) <= self.max_chars,
               f"{len(text)} characters (need {self.min_chars} to "
               f"{self.max_chars})")
        yield ("non-blank", bool(text.strip()),
               "more than white space")
        yield ("no-trailing-space", text == text.rstrip(),
               "no trailing white space")
        yield ("printable",
               all(ch.isprintable() or ch == "\n" for ch in text),
               "no control characters except the one line break")
        lines = text.split("\n")
        yield ("two-parts", len(lines) == 2,
               f"{len(lines)} lines (need exactly 2)")
        if len(lines) == 2:
            to_line, message = lines
            yield ("to-line", to_line.startswith("To: ")
                   and len(to_line) > len("To: "),
                   f"addressee line: {to_line!r}")
            yield ("message-length", 1 <= len(message) <= self.max_msg_chars,
                   f"message is {len(message)} characters (need 1 to "
                   f"{self.max_msg_chars})")
            yield ("message-non-blank", bool(message.strip()),
                   "message more than white space")
            yield ("message-single-line", "\r" not in message,
                   "message is one line")

    def validate(self, text):
        """Fail on the first rule that does not pass; else report."""
        passed = []
        for name, ok, detail in self.rules(text):
            if not ok:
                raise SystemExit(f"gate fail [{name}]: {detail}")
            passed.append(f"{name}={detail}")
        print(f"gate: {'; '.join(passed)}", file=sys.stderr)


def read_entry_bytes():
    """Read entry.txt as raw bytes, exactly as committed."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, ENTRY_FILE), "rb") as fh:
        return fh.read()


def decode_entry(data):
    """Decode the entry bytes as UTF-8, refusing anything else."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"gate fail [utf-8]: {exc}") from exc


def verify_published(path, data):
    """Re-read what was written and refuse a byte mismatch."""
    with open(path, "rb") as fh:
        published = fh.read()
    if published != data:
        raise SystemExit("published entry does not match entry.txt")


def publish(data):
    """Write the bytes unchanged to /output/entry.txt, falling
    back to ./entry.txt, and verify the published bytes match."""
    try:
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "wb") as fh:
            fh.write(data)
        path = OUT_PATH
    except OSError:
        # Never write over the source entry.txt next to this file;
        # use a distinct fallback name in the working directory.
        path = os.path.join(os.getcwd(), "output_entry.txt")
        with open(path, "wb") as fh:
            fh.write(data)
    verify_published(path, data)
    return path


def main():
    data = read_entry_bytes()
    text = decode_entry(data)
    Gate().validate(text)
    path = publish(data)
    print(f"Wrote {len(text)} characters to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

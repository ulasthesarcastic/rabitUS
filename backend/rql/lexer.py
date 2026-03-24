"""RQL Lexer — tokenizes RQL source text."""

import re
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    SOURCE = auto()
    TARGET = auto()
    TRIGGER = auto()
    IF = auto()
    THEN = auto()
    SKIP = auto()
    EVERY = auto()
    MANUAL = auto()
    ARROW = auto()          # →  or  ->
    DOT = auto()
    EQUALS = auto()         # =
    NOT_EQUALS = auto()     # !=
    GT = auto()             # >
    LT = auto()             # <
    IS = auto()
    EMPTY = auto()
    NOT = auto()
    STRING = auto()         # "..."
    NUMBER = auto()
    IDENTIFIER = auto()     # field names, connection refs
    COLON = auto()
    NEWLINE = auto()
    COMMENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int


_KEYWORDS = {
    "SOURCE": TokenType.SOURCE,
    "TARGET": TokenType.TARGET,
    "TRIGGER": TokenType.TRIGGER,
    "IF": TokenType.IF,
    "THEN": TokenType.THEN,
    "SKIP": TokenType.SKIP,
    "EVERY": TokenType.EVERY,
    "MANUAL": TokenType.MANUAL,
    "IS": TokenType.IS,
    "EMPTY": TokenType.EMPTY,
    "NOT": TokenType.NOT,
}

_TOKEN_PATTERNS = [
    (r"#[^\n]*", TokenType.COMMENT),
    (r"→|->", TokenType.ARROW),
    (r"!=", TokenType.NOT_EQUALS),
    (r"=", TokenType.EQUALS),
    (r">", TokenType.GT),
    (r"<", TokenType.LT),
    (r":", TokenType.COLON),
    (r"\.", TokenType.DOT),
    (r'"[^"]*"', TokenType.STRING),
    (r"\d+(\.\d+)?", TokenType.NUMBER),
    (r"[a-zA-Z_][a-zA-Z0-9_/]*", TokenType.IDENTIFIER),
    (r"\n", TokenType.NEWLINE),
    (r"[ \t]+", None),  # skip whitespace
]

_COMPILED = [(re.compile(p), t) for p, t in _TOKEN_PATTERNS]


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    line = 1
    col = 1
    pos = 0

    while pos < len(source):
        matched = False
        for pattern, token_type in _COMPILED:
            m = pattern.match(source, pos)
            if m:
                value = m.group()
                if token_type is not None:
                    if token_type == TokenType.IDENTIFIER and value.upper() in _KEYWORDS:
                        actual_type = _KEYWORDS[value.upper()]
                    else:
                        actual_type = token_type
                    tokens.append(Token(type=actual_type, value=value, line=line, col=col))

                if token_type == TokenType.NEWLINE:
                    line += 1
                    col = 1
                else:
                    col += len(value)
                pos = m.end()
                matched = True
                break

        if not matched:
            raise SyntaxError(f"Unexpected character '{source[pos]}' at line {line}, col {col}")

    tokens.append(Token(type=TokenType.EOF, value="", line=line, col=col))
    return tokens

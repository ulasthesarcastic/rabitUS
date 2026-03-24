"""RQL Parser — builds an AST from tokens."""

from dataclasses import dataclass, field

from backend.rql.lexer import Token, TokenType, tokenize


# ── AST Nodes ──────────────────────────────────────────────

@dataclass
class FieldRef:
    side: str        # "source" or "target"
    field: str


@dataclass
class Mapping:
    source: FieldRef
    target: FieldRef


@dataclass
class Condition:
    left: FieldRef
    operator: str           # ">", "<", "=", "!=", "IS EMPTY", "IS NOT EMPTY"
    right_value: str | None  # None for IS EMPTY / IS NOT EMPTY


@dataclass
class Assignment:
    target: FieldRef
    value: str


@dataclass
class Rule:
    condition: Condition
    action: Assignment | None  # None means SKIP
    is_skip: bool = False


@dataclass
class TriggerDef:
    type: str               # "manual" or "interval"
    interval_minutes: int | None = None


@dataclass
class RQLProgram:
    source: str = ""        # e.g. "api:trendyol/orders"
    target: str = ""        # e.g. "db:logo/tbl_fatura"
    mappings: list[Mapping] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    trigger: TriggerDef = field(default_factory=lambda: TriggerDef(type="manual"))


# ── Parser ──────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, token_type: TokenType) -> Token:
        tok = self.advance()
        if tok.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, got {tok.type.name} ('{tok.value}') "
                f"at line {tok.line}, col {tok.col}"
            )
        return tok

    def skip_newlines(self):
        while self.pos < len(self.tokens) and self.current().type in (TokenType.NEWLINE, TokenType.COMMENT):
            self.advance()

    def parse(self) -> RQLProgram:
        program = RQLProgram()
        self.skip_newlines()

        while self.current().type != TokenType.EOF:
            tok = self.current()

            if tok.type == TokenType.SOURCE:
                self.advance()
                program.source = self._parse_connection_ref()
            elif tok.type == TokenType.TARGET:
                self.advance()
                program.target = self._parse_connection_ref()
            elif tok.type == TokenType.IF:
                program.rules.append(self._parse_rule())
            elif tok.type == TokenType.TRIGGER:
                program.trigger = self._parse_trigger()
            elif tok.type == TokenType.IDENTIFIER:
                # field mapping: source.x → target.y
                program.mappings.append(self._parse_mapping())
            else:
                self.advance()

            self.skip_newlines()

        return program

    def _parse_connection_ref(self) -> str:
        """Parse something like api:trendyol/orders or db:logo/tbl_fatura."""
        parts = []
        parts.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.COLON)
        parts.append(":")
        parts.append(self.expect(TokenType.IDENTIFIER).value)
        return "".join(parts)

    def _parse_field_ref(self) -> FieldRef:
        """Parse source.field_name or target.field_name."""
        side = self.advance().value  # source or target
        self.expect(TokenType.DOT)
        field_name = self.expect(TokenType.IDENTIFIER).value
        return FieldRef(side=side, field=field_name)

    def _parse_mapping(self) -> Mapping:
        """Parse: source.x → target.y"""
        source_ref = self._parse_field_ref()
        self.expect(TokenType.ARROW)
        target_ref = self._parse_field_ref()
        return Mapping(source=source_ref, target=target_ref)

    def _parse_rule(self) -> Rule:
        """Parse: IF source.x > 100 THEN target.y = 'premium'  OR  IF ... THEN SKIP"""
        self.expect(TokenType.IF)
        condition = self._parse_condition()
        self.expect(TokenType.THEN)

        if self.current().type == TokenType.SKIP:
            self.advance()
            return Rule(condition=condition, action=None, is_skip=True)

        # assignment: target.field = value
        target_ref = self._parse_field_ref()
        self.expect(TokenType.EQUALS)
        value = self._parse_value()
        return Rule(
            condition=condition,
            action=Assignment(target=target_ref, value=value),
        )

    def _parse_condition(self) -> Condition:
        left = self._parse_field_ref()

        if self.current().type == TokenType.IS:
            self.advance()
            if self.current().type == TokenType.NOT:
                self.advance()
                self.expect(TokenType.EMPTY)
                return Condition(left=left, operator="IS NOT EMPTY", right_value=None)
            else:
                self.expect(TokenType.EMPTY)
                return Condition(left=left, operator="IS EMPTY", right_value=None)

        op_tok = self.advance()
        op_map = {
            TokenType.GT: ">",
            TokenType.LT: "<",
            TokenType.EQUALS: "=",
            TokenType.NOT_EQUALS: "!=",
        }
        if op_tok.type not in op_map:
            raise SyntaxError(f"Unexpected operator '{op_tok.value}' at line {op_tok.line}")
        operator = op_map[op_tok.type]
        right = self._parse_value()
        return Condition(left=left, operator=operator, right_value=right)

    def _parse_value(self) -> str:
        tok = self.advance()
        if tok.type == TokenType.STRING:
            return tok.value.strip('"')
        if tok.type == TokenType.NUMBER:
            return tok.value
        if tok.type == TokenType.IDENTIFIER:
            return tok.value
        raise SyntaxError(f"Expected value, got {tok.type.name} at line {tok.line}")

    def _parse_trigger(self) -> TriggerDef:
        self.expect(TokenType.TRIGGER)
        if self.current().type == TokenType.MANUAL:
            self.advance()
            return TriggerDef(type="manual")

        self.expect(TokenType.EVERY)
        interval_str = self.expect(TokenType.IDENTIFIER).value  # e.g. "15min", "1hour"

        minutes = _parse_interval(interval_str)
        return TriggerDef(type="interval", interval_minutes=minutes)


def _parse_interval(s: str) -> int:
    s = s.lower()
    if s.endswith("min"):
        return int(s[:-3])
    if s.endswith("hour"):
        return int(s[:-4]) * 60
    raise ValueError(f"Unknown interval format: '{s}'. Use Xmin or Xhour.")


def parse_rql(source: str) -> RQLProgram:
    """High-level helper: source text → RQLProgram."""
    tokens = tokenize(source)
    return Parser(tokens).parse()

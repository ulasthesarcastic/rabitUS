"""Flow executor — runs an RQL program against source/target connectors."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.connectors.api_connector import APIConnector
from backend.connectors.db_connector import DBConnector
from backend.models.connection import Connection
from backend.models.flow import Flow, FlowRun
from backend.rql.parser import RQLProgram, Condition, Rule


class FlowExecutor:
    def __init__(self, db: Session, flow: Flow, program: RQLProgram):
        self.db = db
        self.flow = flow
        self.program = program

    async def run(self) -> FlowRun:
        run = FlowRun(flow_id=self.flow.id, status="running")
        self.db.add(run)
        self.db.commit()

        try:
            records = await self._fetch_source()
            transformed = self._transform(records)
            count = await self._push_target(transformed)

            run.status = "success"
            run.records_processed = count
        except Exception as e:
            run.status = "error"
            run.error_message = str(e)
        finally:
            run.finished_at = datetime.now(timezone.utc)
            self.db.commit()

        return run

    async def _fetch_source(self) -> list[dict[str, Any]]:
        source_conn = self.db.get(Connection, self.flow.source_connection_id)
        if not source_conn:
            raise ValueError("Source connection not found")

        if source_conn.type == "api":
            connector = APIConnector(source_conn)
            return await connector.fetch(self.flow.source_path)
        else:
            connector = DBConnector(source_conn)
            return connector.fetch(self.flow.source_path)

    def _transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply mappings and rules to source records."""
        results = []
        for record in records:
            # Check skip rules first
            if self._should_skip(record):
                continue

            mapped = {}
            # Apply field mappings
            for m in self.program.mappings:
                source_value = record.get(m.source.field)
                mapped[m.target.field] = source_value

            # Apply conditional assignments
            for rule in self.program.rules:
                if rule.is_skip:
                    continue
                if self._evaluate_condition(rule.condition, record) and rule.action:
                    mapped[rule.action.target.field] = rule.action.value

            results.append(mapped)
        return results

    def _should_skip(self, record: dict[str, Any]) -> bool:
        for rule in self.program.rules:
            if rule.is_skip and self._evaluate_condition(rule.condition, record):
                return True
        return False

    def _evaluate_condition(self, cond: Condition, record: dict[str, Any]) -> bool:
        value = record.get(cond.left.field)

        if cond.operator == "IS EMPTY":
            return value is None or value == ""
        if cond.operator == "IS NOT EMPTY":
            return value is not None and value != ""

        right = cond.right_value
        # Try numeric comparison
        try:
            left_num = float(value) if value is not None else 0
            right_num = float(right)
            if cond.operator == ">":
                return left_num > right_num
            if cond.operator == "<":
                return left_num < right_num
            if cond.operator == "=":
                return left_num == right_num
            if cond.operator == "!=":
                return left_num != right_num
        except (ValueError, TypeError):
            pass

        # String comparison
        left_str = str(value) if value is not None else ""
        right_str = str(right) if right is not None else ""
        if cond.operator == "=":
            return left_str == right_str
        if cond.operator == "!=":
            return left_str != right_str
        return False

    async def _push_target(self, records: list[dict[str, Any]]) -> int:
        if not records:
            return 0

        target_conn = self.db.get(Connection, self.flow.target_connection_id)
        if not target_conn:
            raise ValueError("Target connection not found")

        if target_conn.type == "api":
            connector = APIConnector(target_conn)
            await connector.push(self.flow.target_path, records)
            return len(records)
        else:
            connector = DBConnector(target_conn)
            return connector.push(self.flow.target_path, records)

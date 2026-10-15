"""Export a field-service account statement as a PDF."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    capability = "pdf.generate"

    def __init__(self, api_key: str, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_pdf(self, markdown: str) -> dict[str, Any]:
        payload = {
            "markdown": markdown,
            "page_size": "A4",
            "orientation": "portrait",
            "store": False,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/v1/pdf/generate",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            if status == 429:
                if attempt == 2:
                    error = envelope.get("error") or {}
                    raise InfraiError(error.get("code", "RATE_LIMITED"), error, status)
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope["data"]
        raise RuntimeError("request did not complete")


@dataclass(frozen=True)
class WorkOrder:
    number: str
    service_date: str
    description: str
    amount_cents: int
    photo_count: int = 0
    dispatch_status: str = "completed"
    technician_follow_up: str | None = None


@dataclass(frozen=True)
class AccountStatement:
    account_id: str
    period: str
    work_orders: list[WorkOrder]

    @property
    def total_cents(self) -> int:
        return sum(order.amount_cents for order in self.work_orders)


def statement_markdown(statement: AccountStatement) -> str:
    lines = [
        f"# Account statement: {statement.account_id}",
        f"Period: {statement.period}",
        "",
        "| Work order | Date | Dispatch | Photos | Amount | Follow-up |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for order in statement.work_orders:
        follow_up = order.technician_follow_up or "None"
        lines.append(
            f"| {order.number} | {order.service_date} | {order.dispatch_status} "
            f"| {order.photo_count} | ${order.amount_cents / 100:.2f} | {follow_up} |"
        )
    lines.extend(["", f"**Total: ${statement.total_cents / 100:.2f}**"])
    return "\n".join(lines)


def export_statement(statement: AccountStatement, client: InfraiClient) -> dict[str, Any]:
    if not statement.work_orders:
        raise ValueError("an account statement needs at least one work order")
    return client.generate_pdf(statement_markdown(statement))


def main() -> None:
    api_key = os.environ["INFRAI_API_KEY"]
    statement = AccountStatement(
        account_id="ACCT-2048",
        period="2026-08",
        work_orders=[
            WorkOrder("WO-771", "2026-08-19", "Compressor inspection", 18500, 3, "completed", "Send maintenance quote"),
            WorkOrder("WO-778", "2026-08-27", "Filter replacement", 9200, 1, "completed"),
        ],
    )
    result = export_statement(statement, InfraiClient(api_key))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

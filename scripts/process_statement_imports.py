#!/usr/bin/env python3
"""
Normalize imported statement files under storage/imports into a single dataset.

Current support:
- Alipay CSV exports
- WeChat Pay XLSX exports

Known limitation:
- ICBC PDF in this workspace is encrypted and cannot be parsed without a password.
"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IMPORTS_DIR = ROOT / "storage" / "imports"
PROCESSED_DIR = ROOT / "storage" / "processed"
ICBC_PASSWORD_FILE = IMPORTS_DIR / "icbc" / ".password"


CURRENCY_MAP = {
    "人民币": "CNY",
    "澳元": "AUD",
    "美元": "USD",
    "港币": "HKD",
    "日元": "JPY",
    "欧元": "EUR",
    "英镑": "GBP",
}


@dataclass
class Transaction:
    source: str
    source_file: str
    source_format: str
    transaction_time: str
    month: str
    direction: str
    amount: float
    gross_amount: float
    currency: str
    counterparty: str
    description: str
    category: str
    status: str
    payment_method: str
    transaction_type: str
    external_id: str
    merchant_order_id: str
    note: str
    raw: dict


def excel_serial_to_datetime_str(serial_value: str) -> str:
    base = datetime(1899, 12, 30)
    dt = base + timedelta(days=float(serial_value))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_amount(text: str) -> float:
    cleaned = (text or "").replace(",", "").replace("\t", "").strip()
    return float(cleaned or 0)


def get_icbc_password() -> str | None:
    env_password = os.getenv("ICBC_PDF_PASSWORD")
    if env_password:
        return env_password
    if ICBC_PASSWORD_FILE.exists():
        content = ICBC_PASSWORD_FILE.read_text(encoding="utf-8").strip()
        return content or None
    return None


def normalize_signed_amount(direction: str, gross_amount: float) -> float:
    if direction == "income":
        return gross_amount
    if direction == "expense":
        return -gross_amount
    return 0.0


def parse_alipay_csv(path: Path) -> list[Transaction]:
    with path.open("r", encoding="gb18030", newline="") as f:
        rows = list(csv.reader(f))

    header_idx = None
    for idx, row in enumerate(rows):
        if row and row[0] == "交易时间":
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError(f"Could not find Alipay header row in {path.name}")

    header = rows[header_idx]
    items: list[Transaction] = []
    for row in rows[header_idx + 1 :]:
        if not row or len(row) < len(header):
            continue
        data = dict(zip(header, row))
        direction_text = (data.get("收/支") or "").strip()
        direction = {
            "收入": "income",
            "支出": "expense",
            "不计收支": "neutral",
        }.get(direction_text, "unknown")
        gross_amount = parse_amount(data.get("金额", "0"))
        ts = (data.get("交易时间") or "").strip()
        items.append(
            Transaction(
                source="alipay",
                source_file=str(path.relative_to(ROOT)),
                source_format="csv",
                transaction_time=ts,
                month=ts[:7],
                direction=direction,
                amount=normalize_signed_amount(direction, gross_amount),
                gross_amount=gross_amount,
                currency="CNY",
                counterparty=(data.get("交易对方") or "").strip(),
                description=(data.get("商品说明") or "").strip(),
                category=(data.get("交易分类") or "").strip(),
                status=(data.get("交易状态") or "").strip(),
                payment_method=(data.get("收/付款方式") or "").strip(),
                transaction_type=(data.get("交易分类") or "").strip(),
                external_id=(data.get("交易订单号") or "").strip(),
                merchant_order_id=(data.get("商家订单号") or "").strip(),
                note=(data.get("备注") or "").strip(),
                raw=data,
            )
        )
    return items


def parse_wechat_xlsx(path: Path) -> list[Transaction]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as zf:
        shared_strings: list[str] = []
        shared_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        for si in shared_root.findall("a:si", ns):
            text_parts = [node.text or "" for node in si.iterfind(".//a:t", ns)]
            shared_strings.append("".join(text_parts))

        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//a:row", ns):
            values: list[str] = []
            for cell in row.findall("a:c", ns):
                value = cell.find("a:v", ns)
                if value is None:
                    values.append("")
                    continue
                if cell.attrib.get("t") == "s":
                    values.append(shared_strings[int(value.text)])
                else:
                    values.append(value.text or "")
            rows.append(values)

    header_idx = None
    for idx, row in enumerate(rows):
        if row and row[0] == "交易时间":
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError(f"Could not find WeChat header row in {path.name}")

    header = rows[header_idx]
    items: list[Transaction] = []
    for row in rows[header_idx + 1 :]:
        if not row or len(row) < len(header):
            continue
        data = dict(zip(header, row))
        direction_text = (data.get("收/支") or "").strip()
        direction = {
            "收入": "income",
            "支出": "expense",
            "/": "neutral",
        }.get(direction_text, "unknown")
        gross_amount = parse_amount(data.get("金额(元)", "0"))
        ts = excel_serial_to_datetime_str(data.get("交易时间", "0"))
        items.append(
            Transaction(
                source="wechat",
                source_file=str(path.relative_to(ROOT)),
                source_format="xlsx",
                transaction_time=ts,
                month=ts[:7],
                direction=direction,
                amount=normalize_signed_amount(direction, gross_amount),
                gross_amount=gross_amount,
                currency="CNY",
                counterparty=(data.get("交易对方") or "").strip(),
                description=(data.get("商品") or "").strip(),
                category=(data.get("交易类型") or "").strip(),
                status=(data.get("当前状态") or "").strip(),
                payment_method=(data.get("支付方式") or "").strip(),
                transaction_type=(data.get("交易类型") or "").strip(),
                external_id=(data.get("交易单号") or "").strip(),
                merchant_order_id=(data.get("商户单号") or "").strip(),
                note=(data.get("备注") or "").strip(),
                raw=data,
            )
        )
    return items


ICBC_ENTRY_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\n"
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<account>\d+) "
    r"(?P<deposit_type>\S+) "
    r"(?P<seq>\S+) "
    r"(?P<currency>\S+) "
    r"(?P<cash_remit>\S+) "
    r"(?P<summary>\S+) "
    r"(?P<region>\d{4}) "
    r"(?P<signed_amount>[+-][\d,]+\.\d{2}) "
    r"(?P<balance>[\d,]+\.\d{2}) "
    r"(?P<channel>\S+)"
)


def parse_icbc_pdf(path: Path, password: str) -> list[Transaction]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if reader.is_encrypted and reader.decrypt(password) == 0:
        raise ValueError(f"Unable to decrypt ICBC PDF: {path.name}")

    items: list[Transaction] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for match in ICBC_ENTRY_RE.finditer(text):
            data = match.groupdict()
            signed_amount = parse_amount(data["signed_amount"])
            direction = "income" if signed_amount > 0 else "expense"
            currency = CURRENCY_MAP.get(data.get("currency", ""), data.get("currency", "CNY"))
            ts = f"{data['date']} {data['time']}"
            items.append(
                Transaction(
                    source="icbc",
                    source_file=str(path.relative_to(ROOT)),
                    source_format="pdf",
                    transaction_time=ts,
                    month=data["date"][:7],
                    direction=direction,
                    amount=signed_amount,
                    gross_amount=abs(signed_amount),
                    currency=currency,
                    counterparty="",
                    description=data["summary"],
                    category=data["summary"],
                    status="posted",
                    payment_method=f"{data['channel']}|{data['account'][-4:]}",
                    transaction_type=data["summary"],
                    external_id=f"{data['account']}:{ts}:{data['seq']}:{data['balance']}",
                    merchant_order_id="",
                    note="",
                    raw=data,
                )
            )
    return items


def detect_blocked_files(password: str | None) -> list[dict]:
    blocked: list[dict] = []
    for path in sorted((IMPORTS_DIR / "icbc").glob("*.pdf")):
        if not password:
            blocked.append(
                {
                    "source": "icbc",
                    "source_file": str(path.relative_to(ROOT)),
                    "reason": "PDF is encrypted and requires the statement password before text extraction.",
                }
            )
    return blocked


def summarize(transactions: Iterable[Transaction], blocked_files: list[dict]) -> dict:
    txs = list(transactions)
    by_source: dict[str, dict] = {}
    by_month: dict[str, dict] = {}
    top_counterparties: list[dict] = []

    source_groups: dict[str, list[Transaction]] = defaultdict(list)
    for tx in txs:
        source_groups[tx.source].append(tx)

    for source, items in sorted(source_groups.items()):
        by_source[source] = build_metrics(items)

    month_groups: dict[str, list[Transaction]] = defaultdict(list)
    for tx in txs:
        month_groups[tx.month].append(tx)

    for month, items in sorted(month_groups.items()):
        by_month[month] = build_metrics(items)

    counterparty_spend: Counter[str] = Counter()
    for tx in txs:
        if tx.direction == "expense":
            key = tx.counterparty or tx.description or "Unknown"
            counterparty_spend[key] += tx.gross_amount
    for name, amount in counterparty_spend.most_common(20):
        top_counterparties.append({"name": name, "expense": round(amount, 2)})

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files_processed": len({tx.source_file for tx in txs}),
        "transactions_processed": len(txs),
        "blocked_files": blocked_files,
        "by_source": by_source,
        "by_month": by_month,
        "top_counterparties_by_expense": top_counterparties,
    }


def build_metrics(items: Iterable[Transaction]) -> dict:
    income = 0.0
    expense = 0.0
    neutral = 0.0
    counts = Counter()
    for tx in items:
        counts[tx.direction] += 1
        if tx.direction == "income":
            income += tx.gross_amount
        elif tx.direction == "expense":
            expense += tx.gross_amount
        elif tx.direction == "neutral":
            neutral += tx.gross_amount
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(income - expense, 2),
        "neutral": round(neutral, 2),
        "count": sum(counts.values()),
        "counts": dict(counts),
    }


def write_csv(path: Path, txs: list[Transaction]) -> None:
    fieldnames = [
        "source",
        "source_file",
        "source_format",
        "transaction_time",
        "month",
        "direction",
        "amount",
        "gross_amount",
        "currency",
        "counterparty",
        "description",
        "category",
        "status",
        "payment_method",
        "transaction_type",
        "external_id",
        "merchant_order_id",
        "note",
        "raw",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tx in txs:
            row = asdict(tx)
            row["raw"] = json.dumps(row["raw"], ensure_ascii=False)
            writer.writerow(row)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    transactions: list[Transaction] = []
    icbc_password = get_icbc_password()
    for path in sorted((IMPORTS_DIR / "alipay").glob("*.csv")):
        transactions.extend(parse_alipay_csv(path))
    for path in sorted((IMPORTS_DIR / "wechat").glob("*.xlsx")):
        transactions.extend(parse_wechat_xlsx(path))
    if icbc_password:
        for path in sorted((IMPORTS_DIR / "icbc").glob("*.pdf")):
            transactions.extend(parse_icbc_pdf(path, icbc_password))

    transactions.sort(key=lambda tx: tx.transaction_time)
    blocked_files = detect_blocked_files(icbc_password)

    json_path = PROCESSED_DIR / "transactions.normalized.json"
    csv_path = PROCESSED_DIR / "transactions.normalized.csv"
    summary_path = PROCESSED_DIR / "summary.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(tx) for tx in transactions], f, ensure_ascii=False, indent=2)
    write_csv(csv_path, transactions)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summarize(transactions, blocked_files), f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(transactions)} normalized transactions")
    print(json_path.relative_to(ROOT))
    print(csv_path.relative_to(ROOT))
    print(summary_path.relative_to(ROOT))
    if blocked_files:
        print("Blocked files:")
        for blocked in blocked_files:
            print(f"- {blocked['source_file']}: {blocked['reason']}")


if __name__ == "__main__":
    main()

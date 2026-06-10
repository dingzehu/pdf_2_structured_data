#!/usr/bin/env python3
"""Generate synthetic test PDFs for the extraction pipeline."""
import pathlib


def build_pdf(lines: list[str]) -> bytes:
    """Build a minimal valid PDF containing the given text lines."""
    ops = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
    for line in lines:
        safe = (
            line.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        ops.append(f"({safe}) Tj T*")
    ops.append("ET")
    stream = "\n".join(ops).encode()

    obj1 = b"<< /Type /Catalog /Pages 2 0 R >>"
    obj2 = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    obj3 = (
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] "
        b"/Contents 4 0 R "
        b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 "
        b"/BaseFont /Courier >> >> >> >>"
    )
    obj4 = (
        b"<< /Length " + str(len(stream)).encode() + b" >>\n"
        b"stream\n" + stream + b"\nendstream"
    )

    parts: list[bytes] = [b"%PDF-1.4\n"]
    offsets: list[int] = []

    for i, obj in enumerate([obj1, obj2, obj3, obj4], start=1):
        offsets.append(len(b"".join(parts)))
        parts.append(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")

    xref_offset = len(b"".join(parts))
    xref = b"xref\n0 5\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer = (
        b"trailer\n<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n" + str(xref_offset).encode() + b"\n%%EOF\n"
    )

    return b"".join(parts) + xref + trailer


INVOICE_LINES = [
    "INVOICE",
    "",
    "Invoice Number: INV-2024-001",
    "Date: 2024-01-15",
    "Due Date: 2024-02-15",
    "",
    "FROM:",
    "Acme Corporation",
    "123 Business Street",
    "New York, NY 10001",
    "",
    "TO:",
    "John Doe",
    "456 Client Avenue",
    "Los Angeles, CA 90001",
    "",
    "ITEMS:",
    "Description                   Qty   Unit Price      Total",
    "Python Development Services    10      150.00      1500.00",
    "Code Review                     5       80.00       400.00",
    "Technical Documentation         3      100.00       300.00",
    "",
    "SUBTOTAL:                                          2200.00",
    "TAX (10%):                                          220.00",
    "TOTAL DUE:                                         2420.00",
    "",
    "Currency: USD",
    "Payment Terms: Net 30",
]

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent
    path = out / "sample_invoice.pdf"
    path.write_bytes(build_pdf(INVOICE_LINES))
    print(f"Created {path}")

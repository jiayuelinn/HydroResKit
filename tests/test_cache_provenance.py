from pathlib import Path

from hydroreskit.cache import file_metadata, file_sha256
from hydroreskit.provenance import FileAuditRecord, append_file_audit


def test_file_checksum_and_metadata(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("hydroreskit", encoding="utf-8")
    checksum = file_sha256(path)
    metadata = file_metadata(path)
    assert len(checksum) == 64
    assert metadata["sha256"] == checksum
    assert metadata["bytes"] == len("hydroreskit")


def test_append_file_audit(tmp_path):
    source = tmp_path / "table.csv"
    source.write_text("unit_id,x\na,1\n", encoding="utf-8")
    audit = tmp_path / "audit.csv"
    record = FileAuditRecord.create(
        source,
        role="indicator_table",
        source_dataset="demo",
        processing_step="unit-test",
    )
    append_file_audit(record, audit)
    text = audit.read_text(encoding="utf-8")
    assert "indicator_table" in text
    assert "unit-test" in text


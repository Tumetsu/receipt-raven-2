"""SQLAlchemy ORM models for receipts and their items."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.infrastructure.common.orm_types import UTCDateTime


class ReceiptModel(Base):
    """A row of the `receipts` table."""

    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # The job is referenced by id only: deleting old jobs must not touch receipts.
    job_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    payee: Mapped[str] = mapped_column(String(500), nullable=False)
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_sum: Mapped[float] = mapped_column(Float, nullable=False)
    parsed_by: Mapped[str] = mapped_column(String(200), nullable=False)
    source_account: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    document_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_mime_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ocr_notes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, index=True)

    items: Mapped[list["ReceiptItemModel"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="ReceiptItemModel.position",
        lazy="selectin",
    )


class ReceiptItemModel(Base):
    """A row of the `receipt_items` table."""

    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Items keep the order the user gave them.
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    expense_account: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    parsed_by: Mapped[str] = mapped_column(String(200), nullable=False)

    receipt: Mapped[ReceiptModel] = relationship(back_populates="items")

"""Read use case for the receipt list."""

from src.application.common.pagination import Page, PageRequest
from src.application.receipts.queries.receipt_list import (
    ReceiptListItemView,
    ReceiptListQueryProtocol,
)
from src.domain.receipts.entities.receipt import ReceiptStatus


class ListReceiptsUseCase:
    """Serve one page of the receipt list from its query port."""

    def __init__(self, receipt_list_query: ReceiptListQueryProtocol) -> None:
        self.receipt_list_query = receipt_list_query

    async def list_receipts(
        self, page: PageRequest, status: ReceiptStatus | None = None
    ) -> Page[ReceiptListItemView]:
        return await self.receipt_list_query.list_receipts(page, status)

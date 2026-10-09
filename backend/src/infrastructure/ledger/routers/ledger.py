"""API routes for reading the ledger's accounts and payees."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.application.ledger.queries.list_ledger_accounts_use_case import (
    ListLedgerAccountsUseCase,
)
from src.application.ledger.queries.list_ledger_payees_use_case import ListLedgerPayeesUseCase
from src.containers import container
from src.domain.ledger.account import AccountType
from src.infrastructure.common.di import inject_use_case
from src.infrastructure.common.schemas import CollectionResponse, ErrorResponse
from src.infrastructure.ledger.schemas import AccountTypeValue, LedgerAccount

router = APIRouter(
    prefix="/ledger",
    tags=["ledger"],
    responses={502: {"model": ErrorResponse, "description": "The ledger is not available"}},
)


@router.get("/accounts", response_model=CollectionResponse[LedgerAccount])
async def list_ledger_accounts(
    type: Annotated[
        list[AccountTypeValue] | None, Query(description="Only accounts of these types")
    ] = None,
    use_case: ListLedgerAccountsUseCase = Depends(
        inject_use_case(container.ledger.list_ledger_accounts_use_case)
    ),
) -> CollectionResponse[LedgerAccount]:
    accounts = await use_case.list_accounts([AccountType(value) for value in type or []])
    return CollectionResponse(
        items=[LedgerAccount(name=account.name, type=account.type.value) for account in accounts]
    )


@router.get("/payees", response_model=CollectionResponse[str])
async def list_ledger_payees(
    use_case: ListLedgerPayeesUseCase = Depends(
        inject_use_case(container.ledger.list_ledger_payees_use_case)
    ),
) -> CollectionResponse[str]:
    return CollectionResponse(items=await use_case.list_payees())

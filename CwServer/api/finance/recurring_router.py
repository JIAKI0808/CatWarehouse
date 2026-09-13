"""周期性账单（RecurringBill）—— 四个标准端点走通用层，`generate` 保持手写。

`generate_recurring_bills` 是状态机（选出到期的账单 → 记流水 → 按频率推进 `next_date`），
不属于标准 CRUD，原样保留。
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.ledger import Ledger
from models.recurring import RecurringBill
from schemas.recurring import RecurringBillCreate, RecurringBillResponse, RecurringBillUpdate

RECURRING = register_crud(
    CrudSpec(
        name="recurring",
        model=RecurringBill,
        response=RecurringBillResponse,
        path="/recurring",
        id_param="bill_id",
        not_found="Recurring bill not found",
        create=RecurringBillCreate,
        update=RecurringBillUpdate,
        names=CrudNames(
            list="list_recurring",
            create="create_recurring",
            update="update_recurring",
            delete="delete_recurring",
        ),
    )
)

router: APIRouter = build_crud_router(RECURRING)


@router.post("/recurring/generate")
async def generate_recurring_bills(db: AsyncSession = Depends(get_db)):
    now = datetime.now()
    result = await db.execute(
        select(RecurringBill).where(
            RecurringBill.is_active == True,
            RecurringBill.next_date <= now,
        )
    )
    bills = result.scalars().all()
    created = 0

    for bill in bills:
        ledger_item = Ledger(
            amount=bill.amount, date=now, platform=bill.platform,
            description=bill.description, person=bill.person, type=bill.type,
        )
        db.add(ledger_item)

        if bill.frequency == "monthly":
            if bill.next_date.month < 12:
                bill.next_date = bill.next_date.replace(month=bill.next_date.month + 1)
            else:
                bill.next_date = bill.next_date.replace(year=bill.next_date.year + 1, month=1)
        elif bill.frequency == "yearly":
            bill.next_date = bill.next_date.replace(year=bill.next_date.year + 1)
        created += 1

    await db.commit()
    return {"created": created}

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Union, Tuple, Sequence

from sqlalchemy import (
    insert, select, update, delete,
    func, text, Row
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select

from app.db.database import async_session_maker, get_async_session


class AbstractRepository(ABC):
    """
    Базовый абстрактный репозиторий, определяющий методы,
    которые должны быть реализованы в наследниках.
    """

    @abstractmethod
    async def add_one(self, data: dict) -> int:
        """Создать одну запись и вернуть её ID."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> List[Any]:
        """Найти все записи (без фильтров)."""
        raise NotImplementedError

    @abstractmethod
    async def find_all_by_column(self, **filters) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filters) -> Optional[Any]:
        """Найти одну запись по фильтрам. Вернуть None, если не найдено."""
        raise NotImplementedError

    @abstractmethod
    async def remove_one(self, obj_id: int) -> bool:
        """Удалить объект по ID. Вернуть True, если удалён."""
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(self, defaults: dict, **lookup) -> Tuple[Any, bool]:
        """
        Найти объект по lookup. Если нет — создать (defaults + lookup).
        Возвращает (объект, создан_ли).
        """
        raise NotImplementedError

    @abstractmethod
    async def update_or_create(
            self,
            update_data: dict,
            defaults: dict = None,
            **lookup
    ) -> Tuple[Any, bool]:
        """
        Найти объект по lookup. Если есть — обновить, если нет — создать.
        Возвращает (объект, создан_ли).
        """
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, obj_id: int, data: dict) -> Optional[Any]:
        """
        Обновить одну запись по ID.
        Возвращает обновлённый объект (или None, если объект не найден).
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_update(self, items: List[dict], key_field: str = "id") -> int:
        """
        Обновить сразу несколько записей, указанных в items.
        Возвращает количество обновлённых строк.
        """
        raise NotImplementedError

    @abstractmethod
    async def soft_delete(self, obj_id: int, deleted_field: str = "is_deleted") -> bool:
        """
        «Мягкое удаление» (is_deleted=True и т.д.).
        Возвращает True, если обновили запись.
        """
        raise NotImplementedError

    @abstractmethod
    async def restore(self, obj_id: int, deleted_field: str = "is_deleted") -> bool:
        """
        Восстановить «мягко» удалённый объект (is_deleted=False).
        Возвращает True, если обновили запись.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, **filters) -> int:
        """Подсчитать количество записей по фильтрам."""
        raise NotImplementedError

    @abstractmethod
    async def aggregate_min(self, column_name: str, **filters) -> Optional[Any]:
        """Найти минимальное значение по столбцу."""
        raise NotImplementedError

    @abstractmethod
    async def aggregate_max(self, column_name: str, **filters) -> Optional[Any]:
        """Найти максимальное значение по столбцу."""
        raise NotImplementedError

    @abstractmethod
    async def aggregate_avg(self, column_name: str, **filters) -> Optional[float]:
        """Найти среднее значение по столбцу."""
        raise NotImplementedError

    @abstractmethod
    async def aggregate_sum(self, column_name: str, **filters) -> Optional[float]:
        """Найти сумму по столбцу."""
        raise NotImplementedError

    @abstractmethod
    async def group_by_aggregate(
            self,
            group_by_col: str,
            agg_col: str,
            agg_func: Any = func.count,
            **filters
    ) -> List[Dict[str, Any]]:
        """
        Группировка по полю group_by_col и применение agg_func(agg_col).
        Возвращает список словарей [{'group': ..., 'value': ...}, ...].
        """
        raise NotImplementedError

    @abstractmethod
    async def raw_query(self, sql: str, **params) -> List[Any]:
        """
        Выполнить «сырой» SQL (text).
        Возвращает список результатов.
        """
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None  # Переопределите в наследниках

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model.id)
        )
        res = await self.session.execute(stmt)
        new_id = res.scalar_one()
        await self.session.commit()
        return new_id

    async def find_all(self) -> List[Any]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [self._to_dto(row) for row in rows]

    async def find_all_by_column(self, **filters) -> List[Any]:
        stmt = select(self.model).filter_by(**filters)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [self._to_dto(row) for row in rows]

    def _to_dto(self, obj: Any) -> Any:
        if hasattr(obj, "to_read_model"):
            return obj.to_read_model()
        return obj

    async def find_one(self, **filters) -> Optional[Any]:
        stmt = select(self.model).filter_by(**filters)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        return self._to_dto(obj) if obj else None

    async def remove_one(self, obj_id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == obj_id)
        res = await self.session.execute(stmt)
        deleted_count = res.rowcount
        if deleted_count:
            await self.session.commit()
            return True
        return False

    async def get_or_create(
            self,
            defaults: dict,
            **lookup
    ) -> (Any, bool):
        stmt = select(self.model).filter_by(**lookup).limit(1)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if obj:
            return (self._to_dto(obj), False)

        data = {**lookup, **defaults}
        stmt_insert = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
        )
        try:
            insert_res = await self.session.execute(stmt_insert)
            await self.session.commit()
            obj = insert_res.scalar_one()
            return (self._to_dto(obj), True)
        except IntegrityError:
            await self.session.rollback()
            stmt2 = select(self.model).filter_by(**lookup).limit(1)
            res2 = await self.session.execute(stmt2)
            obj2 = res2.scalar_one_or_none()
            if obj2:
                return (self._to_dto(obj2), False)
            raise

    async def update_or_create(
            self,
            update_data: dict,
            defaults: dict = None,
            **lookup
    ) -> (Any, bool):
        if defaults is None:
            defaults = {}

        stmt = select(self.model).filter_by(**lookup).limit(1)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()

        if obj:
            values_to_set = {**update_data}
            stmt_upd = (
                update(self.model)
                .where(self.model.id == obj.id)
                .values(**values_to_set)
                .returning(self.model)
            )
            upd_res = await self.session.execute(stmt_upd)
            await self.session.commit()
            updated_obj = upd_res.scalar_one()
            return (self._to_dto(updated_obj), False)
        else:
            data = {**lookup, **defaults, **update_data}
            stmt_insert = (
                insert(self.model)
                .values(**data)
                .returning(self.model)
            )
            try:
                insert_res = await self.session.execute(stmt_insert)
                await self.session.commit()
                created_obj = insert_res.scalar_one()
                return (self._to_dto(created_obj), True)
            except IntegrityError:
                await self.session.rollback()
                stmt2 = select(self.model).filter_by(**lookup).limit(1)
                res2 = await self.session.execute(stmt2)
                obj2 = res2.scalar_one_or_none()
                if obj2:
                    values_to_set = {**update_data}
                    stmt_upd2 = (
                        update(self.model)
                        .where(self.model.id == obj2.id)
                        .values(**values_to_set)
                        .returning(self.model)
                    )
                    upd_res2 = await self.session.execute(stmt_upd2)
                    await self.session.commit()
                    updated_obj2 = upd_res2.scalar_one()
                    return (self._to_dto(updated_obj2), False)
                raise

    async def bulk_update(self, items: List[dict], key_field: str = "id") -> int:
        if not items:
            return 0

        updated_rows = 0
        for data in items:
            if key_field not in data:
                continue
            obj_id = data[key_field]
            fields_to_update = {k: v for k, v in data.items() if k != key_field}

            stmt = (
                update(self.model)
                .where(getattr(self.model, key_field) == obj_id)
                .values(**fields_to_update)
            )
            res = await self.session.execute(stmt)
            updated_rows += res.rowcount or 0

        if updated_rows:
            await self.session.commit()
        return updated_rows

    async def update_one(self, obj_id: int, data: dict) -> Optional[Any]:
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        updated_obj = res.scalar_one_or_none()

        if updated_obj is not None:
            await self.session.commit()
            return self._to_dto(updated_obj)

        return None

    async def soft_delete(self, obj_id: int, deleted_field: str = "is_deleted") -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values({deleted_field: True})
        )
        res = await self.session.execute(stmt)
        if res.rowcount:
            await self.session.commit()
            return True

        return False

    async def restore(self, obj_id: int, deleted_field: str = "is_deleted") -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values({deleted_field: False})
        )
        res = await self.session.execute(stmt)
        if res.rowcount:
            await self.session.commit()
            return True
        return False

    async def count(self, **filters) -> int:
        stmt = select(func.count(self.model.id)).filter_by(**filters)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def aggregate_min(self, column_name: str, **filters) -> Optional[Any]:
        col = getattr(self.model, column_name)
        stmt = select(func.min(col)).filter_by(**filters)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def aggregate_max(self, column_name: str, **filters) -> Optional[Any]:
        col = getattr(self.model, column_name)
        stmt = select(func.max(col)).filter_by(**filters)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def aggregate_avg(self, column_name: str, **filters) -> Optional[float]:
        col = getattr(self.model, column_name)
        stmt = select(func.avg(col)).filter_by(**filters)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def aggregate_sum(self, column_name: str, **filters) -> Optional[float]:
        col = getattr(self.model, column_name)
        stmt = select(func.sum(col)).filter_by(**filters)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def group_by_aggregate(
            self,
            group_by_col: str,
            agg_col: str,
            agg_func: Any = func.count,
            **filters
    ) -> List[Dict[str, Any]]:
        group_col = getattr(self.model, group_by_col)
        measure_col = getattr(self.model, agg_col)
        stmt = (
            select(group_col, agg_func(measure_col))
            .filter_by(**filters)
            .group_by(group_col)
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        results = []
        for row in rows:
            # row – кортеж (group_value, agg_value)
            results.append({"group": row[0], "value": row[1]})
        return results

    async def raw_query(self, sql: str, **params) -> Sequence[Row[Union[tuple[Any, ...], Any]]]:
        stmt = text(sql)
        res = await self.session.execute(stmt, params)
        return res.fetchall()

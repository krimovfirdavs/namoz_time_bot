import asyncpg
from typing import Optional


class Database:
    def __init__(self, dcs):
        """
        DCS -> database connection string
        """
        self.dcs = dcs
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dcs)

    async def create_user_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                    create table if not exists users (
                        id serial primary key,
                        user_id bigint,
                        username varchar(100),
                        is_admin bool default false,
                        added_at timestamp default current_timestamp
                    );
                """
            )

    async def add_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                    insert into users (user_id, username)
                    values (%d, '%s');
                """ % (user_id, username)
            )

    async def user_exists(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("select * from users where user_id=%d" % user_id)
            return row is not None

    async def is_admin(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("select is_admin from users where user_id=%d" % user_id)
            if row:
                return row["is_admin"]
            return False

    async def count_users(self):
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("select count(*) from users;")
            return result

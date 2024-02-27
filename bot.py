import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs

from motor.motor_asyncio import AsyncIOMotorClient

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.check_user import CheckUser
from tgbot.services import broadcaster

from tgbot.dialogs.captcha.selected.commands import captcha_router
from tgbot.dialogs.captcha import captcha_dialogs
from tgbot.dialogs.profile import profile_dialogs

from infrastructure.database.setup import create_engine, create_metadata, create_session_pool


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Bot started")


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),
        CheckUser()
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.chat_member.outer_middleware(middleware_type)
        dp.my_chat_member.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    engine = create_engine(config.db)
    db_pool = create_session_pool(engine)
    async with engine.begin() as conn:
        await conn.run_sync(create_metadata())

    cluster = AsyncIOMotorClient(config.misc.mongodb_url)
    db = cluster.anonimdb

    dp.include_routers(captcha_router, *captcha_dialogs(), *profile_dialogs())
    setup_dialogs(dp)
    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config, db_pool)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), mdb=db)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped")

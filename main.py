import requests
import logging
from neo4j import GraphDatabase
from menu import menu
from vk_api import get_user_data, get_followers, get_followers_info, get_subscriptions, get_groups_info
from dotenv import load_dotenv
from neo4j_base import save_user, save_group, create_relationship
import os

# Загружаем переменные из .env файла
load_dotenv()

# Получаем значения переменных окружения
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
VK_API_URL = "https://api.vk.com/method/"
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def close_driver():
    driver.close()


def process_user(user_id, level, max_level, logger):
    queue = [(user_id, level)]
    visited = set()

    while queue:
        current_id, current_level = queue.pop(0)

        if current_id in visited or current_level > max_level:
            continue
        visited.add(current_id)

        user_data = get_user_data(current_id)
        if user_data is None or 'response' not in user_data:
            logger.warning(f"Произошла ошибка при получении данных для пользователя {current_id}")
            continue
        user_info = user_data['response'][0]

        with driver.session() as session:
            session.execute_write(save_user, user_info, logger)
            logger.info(f"Добавлен пользователь {user_info['id']} на глубине {current_level}")

            followers_data = get_followers(current_id, logger)
            if followers_data:
                logger.info(f"Найдено {len(followers_data)} подписчиков для пользователя {current_id}")
                follower_ids = followers_data
                followers_info = get_followers_info(follower_ids)
                for follower in followers_info.get('response', []):
                    session.execute_write(save_user, follower, logger)
                    session.execute_write(create_relationship, follower['id'], current_id, "Follow", logger)
                    queue.append((follower['id'], current_level + 1))
                    logger.info(f"Добавлен подписчик {follower['id']} для пользователя {current_id} на глубине {current_level + 1}")
            else:
                logger.info(f"Нет подписчиков для пользователя {current_id}")

            subscriptions_data = get_subscriptions(current_id)
            if 'response' in subscriptions_data and 'items' in subscriptions_data['response']:
                user_group_ids = [sub['id'] for sub in subscriptions_data['response']['items'] if sub.get('type') == 'group']
                if user_group_ids:
                    logger.info(f"Найдено {len(user_group_ids)} подписок на группы для пользователя {current_id}")
                    groups_info = get_groups_info(user_group_ids)
                    for group in groups_info.get('response', []):
                        session.execute_write(save_group, group, logger)
                        session.execute_write(create_relationship, current_id, group['id'], "Subscribe", logger)
                        logger.info(f"Добавлена подписка на группу {group['id']} для пользователя {current_id}")
                else:
                    logger.info(f"Нет подписок на группы для пользователя {current_id}")
            else:
                logger.info(f"Нет данных о подписках на группы для пользователя {current_id}")

        logger.info(f"Глубина {current_level} обработана для пользователя {current_id}. Переход на глубину {current_level + 1}.\n")

    logger.info("Обработка подписчиков и подписок завершена.")


def main():
    if not VK_ACCESS_TOKEN:
        logger.error("Не указан токен. Пожалуйста укажите VK токен")
        return

    user_id_input = input("Введите ID пользователя:")
    user_data = get_user_data(user_id_input)

    if user_data and 'response' in user_data:
        user_info = user_data['response'][0]
        user_id = user_info['id']
        max_level = 2
        process_user(user_id, 0, max_level, logger)
    else:
        logger.error("Не удалось получить данные пользователя")

    menu(driver)
    close_driver()



if __name__ == "__main__":
    main()
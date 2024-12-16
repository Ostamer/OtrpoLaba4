import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем значения переменных окружения
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
VK_API_URL = "https://api.vk.com/method/"

def get_user_data(user_id):
    url = VK_API_URL + "users.get"
    params = {
        "user_ids": user_id,
        "fields": "first_name,last_name,sex,home_town,city",
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params)
    return response.json()


def get_followers(user_id, logger):
    followers = []
    offset = 0
    count = 100

    url = VK_API_URL + "users.getFollowers"
    params = {
        "user_id": user_id,
        "count": 1,
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params).json()
    total_followers = response.get('response', {}).get('count', 0)

    if total_followers > 300:
        logger.info(f"Пропускаем пользователя {user_id}, так как у него более 500 подписчиков.")
        return []

    while offset < total_followers:
        params = {
            "user_id": user_id,
            "count": count,
            "offset": offset,
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131"
        }
        response = requests.get(url, params=params).json()
        items = response.get('response', {}).get('items', [])
        followers.extend(items)

        if not items:
            break

        offset += count

    return followers


def get_followers_info(follower_ids):
    url = VK_API_URL + "users.get"
    params = {
        "user_ids": ",".join(map(str, follower_ids)),
        "fields": "first_name,last_name",
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params)
    return response.json()


def get_subscriptions(user_id):
    url = VK_API_URL + "users.getSubscriptions"
    params = {
        "user_id": user_id,
        "extended": 1,
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params)
    return response.json()


def get_groups_info(group_ids):
    url = VK_API_URL + "groups.getById"
    params = {
        "group_ids": ",".join(map(str, group_ids)),
        "fields": "name,members_count",
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params)
    return response.json()

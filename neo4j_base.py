def save_user(tx, user, logger):
    city = user.get('city', {}).get('title', '')
    home_town = user.get('home_town', '') or city

    tx.run(
        """
        MERGE (u:User {id: $id})
        SET u.screen_name = $screen_name,
            u.name = $name,
            u.sex = $sex,
            u.home_town = $home_town
        """,
        id=user['id'],
        screen_name=user.get('screen_name', ''),
        name=f"{user.get('first_name', '')} {user.get('last_name', '')}",
        sex=user.get('sex', ''),
        home_town=home_town
    )
    logger.info(f"Пользователь {user['id']} добавлен в базу данных.")


def save_group(tx, group, logger):
    tx.run(
        """
        MERGE (g:Group {id: $id})
        SET g.name = $name, 
            g.screen_name = $screen_name,
            g.subscribers_count = $members_count
        """,
        id=group['id'],
        name=group.get('name', ''),
        screen_name=group.get('screen_name', ''),
        members_count=group.get('members_count', 0)
    )
    logger.info(f"Группа {group['id']} добавлена в базу данных.")


def create_relationship(tx, user_id, target_id, rel_type, logger):
    tx.run(
        f"""
        MATCH (u:User {{id: $user_id}})
        MATCH (target {{id: $target_id}})
        MERGE (u)-[:{rel_type}]->(target)
        """,
        user_id=user_id, target_id=target_id
    )
    logger.info(f"Связь {rel_type} создана между {user_id} и {target_id}")

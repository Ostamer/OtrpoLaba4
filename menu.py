def get_total_users(session):
    result = session.run("MATCH (u:User) RETURN count(u) AS total_users")
    print(f"Total users: {result.single()['total_users']}")

def get_total_groups(session):
    result = session.run("MATCH (g:Group) RETURN count(g) AS total_groups")
    print(f"Total groups: {result.single()['total_groups']}")

def get_top_users_by_followers(session, limit):
    result = session.run("""
        MATCH (u:User)<-[:Follow]-(follower:User)
        RETURN u.id AS user_id, u.name AS user_name, count(follower) AS followers_count
        ORDER BY followers_count DESC
        LIMIT $limit
    """, limit=limit)
    print("Top users by followers:")
    for record in result:
        print(f"User ID: {record['user_id']}, Name: {record['user_name']}, Followers: {record['followers_count']}")

def get_top_groups_by_subscribers(session, limit):
    result = session.run("""
        MATCH (g:Group)
        RETURN g.id AS group_id, g.name AS group_name, g.subscribers_count AS subscribers_count
        ORDER BY subscribers_count DESC
        LIMIT $limit
    """, limit=limit)
    print("Top groups by subscribers:")
    for record in result:
        print(f"Group ID: {record['group_id']}, Name: {record['group_name']}, Subscribers: {record['subscribers_count']}")

def get_top_users_by_group_subscriptions(session, limit):
    result = session.run("""
        MATCH (u:User)-[:Subscribe]->(g:Group)
        RETURN u.id AS user_id, u.name AS user_name, COUNT(g) AS group_subscriptions
        ORDER BY group_subscriptions DESC
        LIMIT $limit
    """, limit=limit)
    print("Top users by group subscriptions:")
    for record in result:
        print(f"User ID: {record['user_id']}, Name: {record['user_name']}, Subscriptions: {record['group_subscriptions']}")

def menu(driver):
    while True:
        query_type = input(
            "Выберите параметр меню\n"
            "1 - Суммарное колличество пользователей в бд\n"
            "2 - Суммарное колличество групп в бд\n"
            "3 - Топ пользователей по количеству их подписчиков\n"
            "4 - Топ групп по количеству их подписчиков.\n"
            "5 - Топ пользователей по количеству подписок на группы.\n"
            "Exit - выйти: ")

        if query_type == "Exit":
            print("Завершение работы программы")
            break

        with driver.session() as session:
            match query_type:
                case "1":
                    get_total_users(session)
                case "2":
                    get_total_groups(session)
                case "3":
                    limit = int(input("Введите количество выводимых пользователей по числу их подписчиков: "))
                    get_top_users_by_followers(session, limit)
                case "4":
                    limit = int(input("Введите количество выводимых групп по числу их подписчиков: "))
                    get_top_groups_by_subscribers(session, limit)
                case "5":
                    limit = int(input("Введите количество выводимых пользователей по числу подпискок на группы: "))
                    get_top_users_by_group_subscriptions(session, limit)
                case _:
                    print("Пожалуйста выберете параметр из меню!!!")

# main.py
# -*- coding: utf-8 -*-
"""
Единый файл бота ВКонтакте.
Устанавливаемые зависимости:
    pip install vk_api
"""

import time
import traceback
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError


# ============================================================
#                     НАСТРОЙКИ БОТА
# ============================================================

# ВСТАВЬ СЮДА НОВЫЙ ТОКЕН (старый отзови!)
TOKEN = "vk1.a.yr-65gdFtBQ-1m4A4zw69ASAWlwaiN4Nryiy3H2gZT6U8v_wGpwbTbdpO8HvLtosR7o3DjRhpwBvf6K5YHtdeRptzHaMltIerAkID2iHXA1YCPcI5m4qxmq2zM6U-qcGzMTGL2VYJz-P-Ne7GuGwYOtP_b3BOWuITi1B1UCGiGLaHc7bXCIonRGE-WNkMjSubyUrCPamlKpNayH21lMhow"

# ID сообщества (без минуса)
GROUP_ID = 241611854

# ID создателя (админа). Ему доступны админ-команды
CREATOR_ID = 840976146


# ============================================================
#                     ИНИЦИАЛИЗАЦИЯ
# ============================================================

def create_vk_session():
    """Создаёт сессию VK и объект LongPoll."""
    session = vk_api.VkApi(token=TOKEN)
    longpoll = VkLongPoll(session, group_id=GROUP_ID)
    vk = session.get_api()
    return vk, longpoll


# ============================================================
#                     ОТПРАВКА СООБЩЕНИЙ
# ============================================================

def send_message(vk, user_id, text, keyboard=None, attachment=None):
    """Отправляет сообщение пользователю."""
    try:
        params = {
            "user_id": user_id,
            "message": text,
            "random_id": 0,
        }
        if keyboard is not None:
            params["keyboard"] = keyboard
        if attachment is not None:
            params["attachment"] = attachment
        vk.messages.send(**params)
    except ApiError as e:
        print(f"[API ERROR] Не удалось отправить сообщение {user_id}: {e}")
    except Exception as e:
        print(f"[ERROR] send_message: {e}")


def is_admin(user_id):
    """Проверяет, является ли пользователь создателем."""
    return user_id == CREATOR_ID


# ============================================================
#                     ОБРАБОТКА КОМАНД
# ============================================================

def handle_command(vk, user_id, text):
    """Основная логика бота."""
    text_clean = text.strip()
    text_lower = text_clean.lower()

    # -------- Пользовательские команды --------

    if text_lower in ("начать", "start", "/start", "привет", "hi", "hello"):
        send_message(
            vk, user_id,
            "Привет! Я бот-менеджер бананов 🍌\n"
            "Напиши «помощь», чтобы увидеть список команд."
        )
        return

    if text_lower in ("помощь", "help", "/help"):
        send_message(
            vk, user_id,
            "Доступные команды:\n"
            "/start — приветствие\n"
            "/help — список команд\n"
            "/ping — проверка связи\n"
            "/id — узнать свой ID\n"
            "/admin — админ-панель (только для создателя)"
        )
        return

    if text_lower in ("/ping", "ping"):
        send_message(vk, user_id, "pong 🏓")
        return

    if text_lower in ("/id", "id", "мой id", "мой айди"):
        send_message(vk, user_id, f"Твой ID: {user_id}")
        return

    # -------- Админ-команды (только для создателя) --------

    if text_lower in ("/admin", "admin", "админ"):
        if is_admin(user_id):
            send_message(
                vk, user_id,
                "Админ-панель 👑\n"
                "/stats — статистика бота\n"
                "/say <id> <текст> — отправить сообщение от имени бота\n"
                "/echo <текст> — повторить текст\n"
                "/shutdown — остановить бота (только локально)"
            )
        else:
            send_message(vk, user_id, "⛔ У тебя нет доступа к админ-панели.")
        return

    if text_lower == "/stats":
        if is_admin(user_id):
            send_message(
                vk, user_id,
                f"📊 Статистика бота:\n"
                f"Группа ID: {GROUP_ID}\n"
                f"Создатель ID: {CREATOR_ID}\n"
                f"Статус: онлайн ✅"
            )
        else:
            send_message(vk, user_id, "⛔ Команда только для админа.")
        return

    if text_lower.startswith("/say "):
        if is_admin(user_id):
            parts = text_clean.split(maxsplit=2)
            if len(parts) < 3:
                send_message(vk, user_id, "Использование: /say <id> <текст>")
                return
            try:
                target_id = int(parts[1])
                msg = parts[2]
                send_message(vk, target_id, msg)
                send_message(vk, user_id, f"✅ Сообщение отправлено {target_id}")
            except ValueError:
                send_message(vk, user_id, "❌ ID должен быть числом.")
        else:
            send_message(vk, user_id, "⛔ Команда только для админа.")
        return

    if text_lower.startswith("/echo "):
        if is_admin(user_id):
            echo_text = text_clean[len("/echo "):]
            send_message(vk, user_id, f"🔁 {echo_text}")
        else:
            send_message(vk, user_id, "⛔ Команда только для админа.")
        return

    if text_lower == "/shutdown":
        if is_admin(user_id):
            send_message(vk, user_id, "👋 Останавливаю бота...")
            raise SystemExit
        else:
            send_message(vk, user_id, "⛔ Команда только для админа.")
        return

    # -------- Заглушка для всего остального --------

    send_message(vk, user_id, "Я тебя не понял 🤔 Напиши «помощь».")


# ============================================================
#                     ГЛАВНЫЙ ЦИКЛ
# ============================================================

def main():
    print("Запуск бота...")

    while True:
        try:
            vk, longpoll = create_vk_session()
            print(f"Бот запущен. Группа ID: {GROUP_ID}, создатель: {CREATOR_ID}")

            for event in longpoll.listen():
                if event.type != VkEventType.MESSAGE_NEW:
                    continue
                if not event.to_me:
                    continue

                user_id = event.user_id
                text = event.text or ""

                print(f"[MSG] от {user_id}: {text}")

                try:
                    handle_command(vk, user_id, text)
                except SystemExit:
                    print("Бот остановлен по команде /shutdown.")
                    return
                except Exception as e:
                    print(f"[HANDLER ERROR] {e}")
                    traceback.print_exc()

        except KeyboardInterrupt:
            print("Остановка бота по Ctrl+C.")
            break

        except Exception as e:
            print(f"[LONGPOLL ERROR] {e}")
            traceback.print_exc()
            print("Переподключение через 5 секунд...")
            time.sleep(5)


if __name__ == "__main__":
    main()

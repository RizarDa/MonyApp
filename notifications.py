from plyer import notification


def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="مدیریت موجودی",
            timeout=5
        )
    except Exception:
        pass


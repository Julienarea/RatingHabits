from flask import url_for

DEFAULT_AVATAR_FILENAME = 'default_avatar.png'
AVATAR_FOLDER = 'avatars'  # внутри static


def avatar_url(filename: str | None) -> str:
    """Построить полный URL для аватара по имени файла.
    Если filename пустой или None, используется дефолт.
    """
    if not filename:
        filename = DEFAULT_AVATAR_FILENAME
    # filename хранится без подпапки; добавляем папку avatars
    return url_for('static', filename=f'{AVATAR_FOLDER}/{filename}')


def avatar_storage_path(base_static_path: str, filename: str) -> str:
    """Вернуть абсолютный путь на диске для сохранения файла аватара.
    base_static_path: путь до папки static (app.static_folder).
    """
    import os
    return os.path.join(base_static_path, AVATAR_FOLDER, filename)

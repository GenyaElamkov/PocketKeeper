from sqladmin import Admin

from src.admin.views import UserAdmin


def register_admin_views(admin: Admin) -> Admin:
    """Настройка панели администратора."""
    admin.add_view(UserAdmin)
    return admin

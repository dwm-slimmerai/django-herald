"""
Django app config for herald. Using this to call autodiscover
"""

from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from asgiref.sync import sync_to_async


class HeraldConfig(AppConfig):
    """
    Django app config for herald. Using this to call autodiscover
    """

    name = 'herald'

    def ready(self):
        from herald import registry

        self.module.autodiscover()

        Notification = self.get_model('Notification')

        try:
            # add any new notifications to database.
            for index, klass in enumerate(registry._registry):
                notification, created = async_get_or_create(klass)

                if not created:
                    notification.verbose_name = sync_to_async(
                        klass.get_verbose_name)()
                    notification.can_disable = sync_to_async(
                        klass.can_disable)
                    sync_to_async(notification.save)()

        except OperationalError:
            # if the table is not created yet, just keep going.
            pass
        except ProgrammingError:
            # if the database is not created yet, keep going (ie: during testing)
            pass


async def async_get_or_create(klass):
    notification, created = await sync_to_async(
        Notification.objects.get_or_create)(
        notification_class = klass.get_class_path(),
        defaults = {
            'verbose_name': klass.get_verbose_name(),
            'can_disable': klass.can_disable,
        }
    )

    return notification, created

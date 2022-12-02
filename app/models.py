from django.db import models


class LeadState(models.Model):
    STATE_NEW = 1
    STATE_IN_PROGRESS = 2
    STATE_POSTPONED = 3
    STATE_DONE = 4

    name = models.CharField(
        u"Название",
        max_length=50,
        unique=True,
    )


class Lead(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=u"Имя",
    )
    transit = models.CharField(
        max_length=255,
        verbose_name=u"История последнего перехода",
        null=True
    )
    state = models.ForeignKey(
        LeadState,
        on_delete=models.PROTECT,
        default=LeadState.STATE_NEW,
        verbose_name=u"Состояние",
    )

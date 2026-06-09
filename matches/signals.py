from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Match


@receiver(pre_save, sender=Match)
def match_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Match.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Match.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    if created:
        return
    if instance.status != 'finalizado':
        return
    if instance.home_score is None or instance.away_score is None:
        return
    from predictions.models import Prediction
    for pred in Prediction.objects.filter(match=instance).select_related('pool'):
        pred.points = calculate_points(
            pred.home_score, pred.away_score,
            instance.home_score, instance.away_score,
        )
        pred.save(update_fields=['points', 'updated_at'])


def calculate_points(pred_h, pred_a, actual_h, actual_a):
    if pred_h == actual_h and pred_a == actual_a:
        return 3
    pred_diff = pred_h - pred_a
    actual_diff = actual_h - actual_a
    if pred_diff == 0 and actual_diff == 0:
        return 1
    if pred_diff != 0 and actual_diff != 0 and (pred_diff > 0) == (actual_diff > 0):
        return 1
    return 0

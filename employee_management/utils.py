from management import models as management_models


def get_unread_messages(sender, receiver, is_group=False):
    unread_messages = 0
    receiver_objs = management_models.ReceiverGroup.objects.filter(users=receiver, is_group=is_group)
    for receiver_obj in receiver_objs:
        messages = management_models.Message.objects.filter(receiver=receiver_obj, sender=sender).order_by(
            'created_at')
        for message in messages:
            if not message.is_read:
                unread_messages += 1
    return unread_messages




def mark_messages_as_read(sender, receiver, is_group=False):
    print("marking messages as read", sender, receiver)
    receiver_objs = management_models.ReceiverGroup.objects.filter(users=receiver, is_group=is_group)
    for receiver_obj in receiver_objs:
        messages = management_models.Message.objects.filter(receiver=receiver_obj, sender=sender).order_by(
            'created_at')
        for message in messages:

            if not message.is_read:
                message.is_read = True
                message.save()
    return True




def get_group_unread_messages(request, group):
    count = 0
    receiver_obj = management_models.ReceiverGroup.objects.get(id=group, is_group=True)
    messages = management_models.Message.objects.filter(receiver=receiver_obj).order_by('created_at')
    for message in messages:
        if message.sender.user_id != request.user.id:
            if not message.is_read:
                count += 1
    return count






def mark_group__messages_as_read(request, group):
    receiver_obj = management_models.ReceiverGroup.objects.get(id=group, is_group=True)
    messages = management_models.Message.objects.filter(receiver=receiver_obj).order_by('created_at')
    for message in messages:
        if message.sender.user_id != request.user.id:
            if not message.is_read:
                message.is_read = True
                message.save()
    return True
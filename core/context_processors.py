def core(request):
    user = request.user
    if user.is_authenticated:
        notifications = user.notifications.filter(is_read=False).order_by('is_read', '-created')

        return {
            'notifications': notifications[:5],
            'more_notifications': notifications.count() > 5,
        }
    return {}

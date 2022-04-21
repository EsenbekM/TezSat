class NotificationAction:
    """Notification action"""
    ACTIVATED = "activated"
    STARED = "stared"
    BLOCKED = "blocked"
    PAYMENT = 'payment'

    """PushNotification action"""
    BUSINESS = 'business'
    REGULAR_USER = 'regular_user'
    EVERYONE = 'everyone'

    @classmethod
    def choices(cls):
        return (
            (cls.ACTIVATED, cls.ACTIVATED),
            (cls.STARED, cls.STARED),
            (cls.BLOCKED, cls.BLOCKED),
            (cls.PAYMENT, cls.PAYMENT),
        )

    @classmethod
    def push_choices(cls):
        return (
            (cls.BUSINESS, cls.BUSINESS),
            (cls.REGULAR_USER, cls.REGULAR_USER),
            (cls.EVERYONE, cls.EVERYONE),
        )
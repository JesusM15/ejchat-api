# social_api/authentication.py

from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class EmailBackend:
    def authenticate(self, request, email=None, password=None):
        logger.debug(f"Trying to authenticate user with email: {email}")
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            logger.warning(f"User with email {email} does not exist.")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

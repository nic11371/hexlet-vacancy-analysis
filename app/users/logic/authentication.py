from django.contrib.auth.backends import ModelBackend

from django.contrib.auth import get_user_model


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                return user
        except (UserModel.DoesNotExist,UserModel.MultipleObjectsReturned):
            return None

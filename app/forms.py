import logging

from django import forms
from django.conf import settings
from django.forms import ModelForm

from app.models import ExtendedUser, UserFiles

logger = logging.getLogger(__name__)


class ExtendedUserForm(ModelForm):
    first_name = forms.CharField(required=False, max_length=100)
    last_name = forms.CharField(required=False, max_length=100)

    class Meta:
        model = ExtendedUser
        fields = ['email', 'first_name', 'last_name', 'password']


class UserFilesForm(ModelForm):

    def clean_uploaded_file(self):
        logger.info('Inside clean_uploaded_file.')
        uploaded_file = self.cleaned_data['uploaded_file']
        content_type = uploaded_file.content_type
        logger.info("File's content-type is {!r}.".format(content_type))
        types = ', '.join(settings.CONTENT_TYPES)
        if content_type not in settings.CONTENT_TYPES:
            logger.error('Invalid content type. Allowed content-types are: {}.'.format(format(types)))
            raise forms.ValidationError('Content-type should one of {!r}'.format(types))
        logger.info('Content-type was fine.')
        return uploaded_file

    class Meta:
        model = UserFiles
        fields = ['userid', 'uploaded_file']

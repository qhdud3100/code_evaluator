import os
import string
import random
import uuid

from django.utils.deconstruct import deconstructible


def generate_random(type='char', length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@deconstructible
class FilenameChanger(object):

    def __init__(self, base_path, ext=None):
        self.base_path = base_path
        self.ext = ext

    def __call__(self, instance, filename, *args, **kwargs):
        splits = filename.split('.')
        if len(splits) > 1:
            ext = splits[-1].lower()
        else:
            ext = self.ext
        filename = "%s.%s" % (uuid.uuid4(), ext)

        return os.path.join(self.base_path, filename)

    def __eq__(self, other):
        return self.base_path

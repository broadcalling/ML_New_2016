from django.utils.translation import ugettext as _
from django.core import exceptions
import os
import time
import random
import urllib
from datetime import datetime
from pytz import UTC
from django.core.files.storage import get_storage_class


def store_uploaded_file(request, file_key, allowed_file_types, max_file_size, base_storage_filename):

    if file_key not in request.FILES:
        raise ValueError(_("No file uploaded with key '" + file_key + "'."))

    uploaded_file = request.FILES[file_key]
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if not file_extension in allowed_file_types:
        file_types = "', '".join(allowed_file_types)
        msg = _("Allowed file types are '{file_types}'.").format(file_types=file_types)
        raise exceptions.PermissionDenied(msg)

    new_file_name = base_storage_filename + file_extension

    file_storage = get_storage_class()()
    # use default storage to store file
    file_storage.save(new_file_name, uploaded_file)
    # check file size
    size = file_storage.size(new_file_name)
    if size > max_file_size:
        file_storage.delete(new_file_name)
        msg = _("Maximum upload file size is {file_size} bytes.").format(file_size=max_file_size)
        raise exceptions.PermissionDenied(msg)

    return file_storage, new_file_name


def course_and_time_based_filename_generator(course_id, base_name):
    """
    Generates a filename (without extension) based on the current time and the supplied filename.

    Args:
        course_id (object): A course identification object that must support conversion to unicode.
        base_name (str): A name describing what type of file this is. Should not include any characters
            that are not safe for filenames.

    Returns:
        str: a concatenation of the course_id (with backslashes replace by underscores), the base_name,
            and the current time. Note that there will be no extension.

    """
    return u"{course_prefix}_{base_name}_{timestamp_str}".format(
        course_prefix=urllib.quote(unicode(course_id).replace("/", "_")),
        base_name=base_name,
        timestamp_str=datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    )
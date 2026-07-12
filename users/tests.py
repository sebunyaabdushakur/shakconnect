from django.conf import settings
from django.test import SimpleTestCase


class ProfileImageStorageConfigurationTest(SimpleTestCase):
    def test_profile_photo_uploads_use_cloudinary_storage(self):
        self.assertEqual(
            settings.DEFAULT_FILE_STORAGE,
            'cloudinary_storage.storage.MediaCloudinaryStorage'
        )
        self.assertIn('cloudinary_storage', settings.INSTALLED_APPS)

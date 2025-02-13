from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import numpy as np

class User(AbstractUser):
    face_encoding = models.BinaryField(null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_face_encoding(self, encoding):
        self.face_encoding = encoding.tobytes()
    
    def get_face_encoding(self):
        return np.frombuffer(self.face_encoding)

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-check_in_time']
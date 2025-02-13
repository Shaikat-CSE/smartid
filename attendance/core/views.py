# core/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import User, Attendance
from .utils.face_detection import FaceDetector
from .utils.liveness import LivenessDetector
import numpy as np
import base64
import cv2

logger = logging.getLogger(__name__)

class LandingView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'landing.html')

class RegistrationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'register.html')

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'login.html')

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('landing')

class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def get(self, request):
        attendance_records = Attendance.objects.filter(user=request.user).order_by('-check_in_time')[:30]
        return render(request, 'dashboard.html', {
            'attendance_records': attendance_records
        })

class FaceRegistrationAPI(APIView):
    def _process_image_data(self, image_data):
        # Remove data:image/jpeg;base64, prefix if present
        if ';base64,' in image_data:
            image_data = image_data.split(';base64,')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    def post(self, request):
        try:
            # Convert base64 image to numpy array
            image_array = self._process_image_data(request.data['image'])
            
            # Check liveness
            liveness_detector = LivenessDetector()
            if not liveness_detector.detect_liveness(image_array):
                return Response({'error': 'Liveness check failed. Please use a real face.'}, status=400)
            
            # Get face encoding
            face_detector = FaceDetector()
            face_encoding = face_detector.get_face_encoding(image_array)
            
            # Check for duplicate faces
            existing_users = User.objects.exclude(face_encoding=None)
            existing_encodings = [user.get_face_encoding() for user in existing_users]
            
            if face_detector.find_duplicate_face(face_encoding, existing_encodings):
                return Response({'error': 'This face is already registered in the system.'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=request.data['username'],
                first_name=request.data['name']
            )
            user.set_face_encoding(face_encoding)
            user.save()
            
            messages.success(request, 'Registration successful! You can now login.')
            return Response({'message': 'Registration successful'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class FaceLoginAPI(APIView):
    def _process_image_data(self, image_data):
        try:
            if not image_data:
                raise ValueError("No image data provided")
                
            # Remove data:image/jpeg;base64, prefix if present
            if ';base64,' in image_data:
                image_data = image_data.split(';base64,')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Error processing image data: {str(e)}")
            raise

    def post(self, request):
        try:
            if 'image' not in request.data:
                return Response(
                    {'error': 'No image data provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_array = self._process_image_data(request.data['image'])
            
            if image_array is None:
                return Response(
                    {'error': 'Invalid image data'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get face encoding
            face_detector = FaceDetector()
            face_encoding = face_detector.get_face_encoding(image_array)
            
            if face_encoding is None:
                logger.warning("No face detected or could not generate encoding")
                return Response(
                    {'error': 'No face detected or face is not clear. Please try again.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find matching user
            users = User.objects.filter(is_active=True)
            for user in users:
                stored_encoding = user.get_face_encoding()
                if stored_encoding is not None and face_detector.verify_face(stored_encoding, face_encoding):
                    login(request, user)
                    Attendance.objects.create(user=user)
                    return Response({
                        'success': True,
                        'message': f'Welcome back, {user.first_name}!'
                    })
            
            return Response(
                {'error': 'Face not recognized. Please try again or register.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': 'An error occurred during face recognition. Please try again.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
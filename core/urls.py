# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObtainUserFromTokenView, UserRegisterAPIView, FollowCreateView, FollowDeleteView, FriendshipListView, UserViewSet, UserProfileUpdateView, UserSearchView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('user/', ObtainUserFromTokenView.as_view(), name='get_user'),
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('user/profile/', UserProfileUpdateView.as_view(), name='user_profile_update'),

    
    # seguidos y amistades
    path('profiles/follow/', FollowCreateView.as_view(), name='follow_create'),
    path('profiles/follow/<int:pk>/', FollowDeleteView.as_view(), name='follow_delete'),
    path('profiles/friendships/', FriendshipListView.as_view(), name='friendship_list'),
    
    #userActions
    path('user/actions/', include(router.urls)),
    
    path('search/users/', UserSearchView.as_view(), name='user-search'),
]


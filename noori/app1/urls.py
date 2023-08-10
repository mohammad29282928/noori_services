from django.urls                     import path, include
from django.conf.urls.static         import static
from django.conf                     import settings


from .views                          import UserLoginView, UserLogoutView
from .view.user                      import UserListView, UserAddView, UserDeleteView, UserEditView

urlpatterns = [
    path('api/user_login/',          UserLoginView.as_view(),      name = 'user_login'),
    path('api/user_logout/',         UserLogoutView.as_view(),     name = 'user_logout'),

    path('api/list_user/',           UserListView.as_view(),       name = 'list_user'),
    path('api/add_user/',            UserAddView.as_view(),        name = 'add_user'),
    path('api/del_user/',            UserDeleteView.as_view(),     name = 'del_user'),
    path('api/edit_user/',           UserEditView.as_view(),       name = 'edit_user'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
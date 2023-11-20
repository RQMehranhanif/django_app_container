from django.urls import path
from .views import about, contact,hello_world, index, service
# excel_db,

urlpatterns = [
    path('index/', index, name='index'),
    path('hello/', hello_world, name='hello_world'),
    path('service/', service, name='service'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    # path('excel_db/', excel_db, name='excel_db'),
]



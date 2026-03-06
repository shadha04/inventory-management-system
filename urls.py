"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reg/', views.register,name='reg'),
    path('log/',views.log,name='log'),
    path('ad/',views.admin,name='ad'),
    path('cs/',views.customer,name='cs'),
    path('',views.home),
    path('addpr/',views.add_product,name='addpr'),
    path('edit_product/<int:id>',views.edit_product,name='edit_product'),
    path('details/<int:id>',views.product_details,name='details'),
    path('del_product/<int:id>',views.del_product,name='del_product'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('low-stock/', views.low_stock_products, name='low_stock_products'),
    path('expired/', views.expired_products, name='expired_products'),
    path('view_cat',views.view_categories,name='view_cat'),
    path('report',views.report,name='report'),
    path('view_customer',views.view_customer,name='view_customer'),
    path('order/<int:id>',views.order,name='order'),
    path('my_orders',views.my_orders,name='my_orders'),
    path('view_order',views.view_order,name='view_order'),
    path('changepass',views.change_psss,name='changepass'),
    path('view_profile/',views.view_profile,name='view_profile'),
    path('edit_profile/<int:id>/',views.edit_profile,name='edit_profile'),
    path('category_products/<int:id>/', views.category_products, name='category_products'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('place_order/<int:id>/', views.place_order, name='place_order'),
    path('update_quantity/<int:id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('order_page/<int:id>/', views.order_page, name='order_page'),
    path('confirm_order/<int:id>/', views.confirm_order, name='confirm_order'),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

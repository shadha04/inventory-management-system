from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone

# Create your models here.
class Profile(AbstractUser):
    usertype=models.CharField(max_length=20,null=False,blank=False)

class Customer(models.Model):
    Customer_id=models.ForeignKey(Profile,on_delete=models.CASCADE)
    address=models.CharField(max_length=40)
    confirm_pass=models.CharField(max_length=20)
    ph_no=models.IntegerField()
    image=models.ImageField(upload_to='customer_images/',null=True,blank=True)


class Category(models.Model):
    name=models.CharField(max_length=200)


class Product(models.Model):
    Category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    quantity=models.IntegerField()
    price=models.IntegerField()
    discription=models.CharField(max_length=2000)
    exp_date=models.DateField()
    image=models.ImageField(upload_to='media/')
    def law_stock(self):
        return self.quantity<=5
    def is_exp(self):
        if self.exp_date:
            return self.exp_date< datetime.date.today()
        return False
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(default=timezone.now)   # stores exact timestamp
    status = models.CharField(max_length=200, default='Pending')
    address = models.TextField( blank=True, null=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        
    ]

    PAYMENT_METHODS = [
        ('COD', 'Cash on delivery'),
        ('Online', 'Online'),
    ]

    PAYMENT_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Unpaid')

    @property
    def total_price(self):
        return self.quantity * self.product.price
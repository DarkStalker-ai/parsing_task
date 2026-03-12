from django.db import models

# Create your models here.
class Product(models.Model):

    full_name = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    memory = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)

    default_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    reviews_count = models.IntegerField(default=0)

    screen_diagonal = models.CharField(max_length=255, blank=True, null=True)
    display_resolution = models.CharField(max_length=255, blank=True, null=True)

class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.URLField(max_length=255, blank=True, null=True)

class Product_Characteristics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics')
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
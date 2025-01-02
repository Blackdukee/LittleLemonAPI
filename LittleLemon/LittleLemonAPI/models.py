from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title


# Create your models here.
class MenuItem(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True, default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.title + ' - ' + str(self.price) + ' - ' + str(self.featured) + ' - ' + self.category.title

class Cart(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        unique_together = ('user', 'menuitem',)
        
class Order(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True,  null=True) # type: ignore
    total = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(db_index=True)

class OrderItem(models.Model):
    order = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'menuitem',)

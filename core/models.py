from django.conf import settings
from django.db import models
from django.shortcuts import reverse


# Create your models here.


CATEGORIES = (
	('S', 'shirt'),
	('D', 'dress'),
	('O', 'out wear')
)
LABELS = (
	('P', 'primary'),
	('S', 'secondary'),
	('D', 'danger')
)
class Item(models.Model):
	title = models.CharField(max_length = 100)
	price = models.FloatField()
	category = models.CharField(choices = CATEGORIES, max_length = 2 )
	label = models.CharField(choices = LABELS , max_length  = 2 )
	discount_price = models.FloatField(null = True, blank = True)
	description = models.TextField(default="this is the description")

	def __str__(self):
		return self.title
	
	def get_absolute_url(self):
       		return reverse("core:product", kwargs={'slug': self.slug})

	def get_add_to_cart_url(self):
        	return reverse("core:add-to-cart", kwargs={'slug': self.slug
        })

	def get_remove_from_cart_url(self):
        	return reverse("core:remove-from-cart", kwargs={'slug': self.slug
        })

class OrderItem(models.Model):
	quantity = models.IntegerField(default= 1)
	item = models.ForeignKey(Item, on_delete = models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
	ordered = models.BooleanField(default= False)

	def __str__(self):
		return self.title

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add = True)
	Ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default= False)

	def __str__(self):
		return self.user.username


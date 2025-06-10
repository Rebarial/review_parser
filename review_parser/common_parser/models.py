from django.db import models
from django.utils.timezone import now


class Organization(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    inn = models.CharField(max_length=12, null=True, blank=True)
    
    def __str__(self):
        return self.title or f'Организация #{self.id}'


class Branch(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="branches"
    )
    address = models.TextField()
    yandex_map_link = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.organization}: {self.address[:50]} : {self.yandex_map_link}'


class Review(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="reviews")
    author = models.CharField(max_length=255)
    avatar = models.URLField(null=True, blank=True)
    published_date = models.DateTimeField(default=now)
    rating = models.PositiveSmallIntegerField()
    content = models.TextField()
    
    def __str__(self):
        return f"{self.author}'s review for {self.branch}"
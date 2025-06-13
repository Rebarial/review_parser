from django.db import models
from django.utils.timezone import now


class Organization(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    inn = models.CharField(max_length=12, null=True, blank=True)
    
    def __str__(self):
        return self.name or f'Организация #{self.id}'


class Branch(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="branches"
    )
    address = models.TextField()
    yandex_map_url = models.URLField(max_length=500, null=True, blank=True)
    twogis_map_url = models.URLField(max_length=500, null=True, blank=True)
    vlru_url = models.URLField(max_length=500, null=True, blank=True)
    twogis_review_count = models.IntegerField(null=True, blank=True)
    twogis_review_avg = models.FloatField(null=True, blank=True)
    vlru_review_count = models.IntegerField(null=True, blank=True)
    vlru_review_avg = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.id} : {self.organization}: {self.address[:50]}'


class Review(models.Model):

    PROVIDER_CHOICES = [
        ('yandex', 'Яндекс'),
        ('google', 'Гугл'),
        ('2gis', '2GIS'),
        ('vlru', 'VL.RU')
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="reviews")
    author = models.CharField(max_length=255)
    avatar = models.URLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    photos = models.TextField(null=True, blank=True)
    published_date = models.DateTimeField(default=now)
    rating = models.PositiveSmallIntegerField()
    content = models.TextField()
    
    provider = models.CharField(
        max_length=10,
        choices=PROVIDER_CHOICES,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.author}'s review for {self.branch}"
    


class BranchIPMapping(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='ip_mappings'
    )
    ip_address = models.GenericIPAddressField()
    
    def __str__(self):
        return f"{self.ip_address} → Филиал {self.branch.id} : {self.branch.address}"
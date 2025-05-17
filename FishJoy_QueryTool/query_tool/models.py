from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Spots(models.Model):
    title = models.CharField(max_length=50, verbose_name='Spot name')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')
    location = models.CharField(max_length=50)
    max_depth = models.FloatField(validators=[MaxValueValidator(10000), MinValueValidator(1)], verbose_name='Max depth')
    fish = models.ManyToManyField('Fish', symmetrical=False)
    spot_category = models.ForeignKey('SpotCategory', on_delete=models.PROTECT)

    def __str__(self):
        return self.title

    def class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('spot', kwargs={'spot_slug': self.slug})

    def get_edit_url(self):
        return reverse('spots-detail', args=[self.pk])

    class Meta:
        verbose_name = 'Spot'
        verbose_name_plural = 'Spots'
        ordering = ['title']


class Fish(models.Model):
    name = models.CharField(max_length=50, verbose_name='Fish name')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')
    average_weight = models.FloatField(validators=[MaxValueValidator(200.0), MinValueValidator(0.1)], verbose_name='Average weight')
    baits = models.ManyToManyField('Baits', symmetrical=False)
    fish_category = models.ForeignKey('FishCategory', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('single_fish', kwargs={'single_fish_slug': self.slug})

    def get_edit_url(self):
        return reverse('fish-detail', args=[self.pk])

    class Meta:
        verbose_name = 'Fish'
        verbose_name_plural = 'Fish'
        ordering = ['name']


class Baits(models.Model):
    name = models.CharField(max_length=50, verbose_name='Bait name')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')
    price = models.FloatField(validators=[MaxValueValidator(100000), MinValueValidator(0)])

    def __str__(self):
        return self.name

    def class_name(self):
        return self.__class__.__name__

    def get_edit_url(self):
        return reverse('baits-detail', args=[self.pk])

    class Meta:
        verbose_name = 'Bait'
        verbose_name_plural = 'Baits'
        ordering = ['name']


class SpotCategory(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name='Spot category')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('spots_category', kwargs={'spots_category_slug': self.slug})

    class Meta:
        verbose_name = 'Spot category'
        verbose_name_plural = 'Spot categories'
        ordering = ['name']


class FishCategory(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name='Fish category')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('fish_category', kwargs={'fish_category_slug': self.slug})

    class Meta:
        verbose_name = 'Fish category'
        verbose_name_plural = 'Fish categories'
        ordering = ['name']

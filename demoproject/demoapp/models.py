from django.db import models

class Person(models.Model):
    fname = models.CharField("First name", max_length=200)
    lname = models.CharField("Last name", max_length=200)
    email = models.EmailField("Email")
    sdate = models.DateField("Start date")

class Equipment(models.Model):
    person = models.ForeignKey(Person)
    name = models.CharField("Equipment", max_length=200)

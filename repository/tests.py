from django.test import TestCase

# Create your tests here.
import hashlib

md5 = hashlib.md5()
md5.update('abc123'.encode('utf-8'))
print (md5.hexdigest())
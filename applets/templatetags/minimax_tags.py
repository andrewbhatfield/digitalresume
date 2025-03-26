from django import template

register = template.Library()

def two_d_to_one_d(i,j):
    i = int(i)
    j = int(j)
    return str(3*i + j)

register.filter(two_d_to_one_d)
from django import template

register = template.Library()

def cellId(col,row):
    return 10*(row-1)+(col-1)

register.filter(cellId)
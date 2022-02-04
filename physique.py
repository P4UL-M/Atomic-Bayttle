from math import cos, sin

g=9.806 *0.5

def get_x(t, v0, a):
    return v0*t*cos(a)*5

def get_y(x, v0, a, h0):
    if cos(a)==0:
        b=1
        c=1
    else:
        c=x/(cos(a)*v0)
        b=x/cos(a)

    return -(-(g/2) * c**2 + v0*sin(a)*b)+ h0
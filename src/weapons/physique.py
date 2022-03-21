from math import cos, sin, pi

g=9.806 *0.5

def get_x(t, v0, a):
    a=a*(pi/180)*0.2
    return v0*t*cos(a)*5

def get_y(x, v0, a, h0):
    a=a*(pi/180)*0.2
    if cos(a)==0:
        b=1
        c=1
    else:
        c=x/(cos(a)*v0)
        b=x/cos(a)
    #print("y :", -(-(g/2) * c**2 + v0*sin(a)*b), " c :",c, " b :",b, " x :", x)
    return -(-(g/2) * c**2 + v0*sin(a)*b)+ h0
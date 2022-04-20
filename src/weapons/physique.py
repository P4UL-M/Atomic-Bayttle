from math import cos, tan, pi

g = 9.806


class trajectoire:
    def __init__(self, pos, angle, force) -> None:
        self.pos0 = pos
        self.angle = angle
        self.force = force

    def get_x(self, t):
        a = self.angle
        return t * self.force * cos(a)

    def get_y(self, x):
        a = self.angle
        return x * tan(a) - (g * x**2) / (2 * self.force**2 * cos(a)**2)

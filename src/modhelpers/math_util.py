class MathUtils:
    @staticmethod
    def lerp(begin: float, end: float, factor: float):
        # Linear interpolation
        return (1 - factor) * begin + factor * end

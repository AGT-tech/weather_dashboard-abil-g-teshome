from typing import List

class TrendDetector:
    @staticmethod
    def detect_trend(temps: List[int]) -> str:
        """
        Determine the trend of temperatures using simple linear regression.

        Args:
            temps (List[int]): List of temperature values.

        Returns:
            str: One of 'rising', 'falling', or 'stable'.
        """
        n = len(temps)
        if n < 2:
            return "stable"  # Not enough data to detect a trend

        x = list(range(n))
        y = temps

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x) ** 2 for xi in x)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "rising"
        else:
            return "falling"

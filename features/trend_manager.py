import logging
from typing import List

logger = logging.getLogger(__name__)

class TrendDetector:
    """
    Provides functionality to detect the trend (rising, falling, or stable)
    in a list of temperature values using simple linear regression.
    """

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
            logger.info("Not enough data to detect trend, returning 'stable'")
            return "stable"  # Not enough data to detect a trend

        x = list(range(n))
        y = temps

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x) ** 2 for xi in x)

        logger.debug(f"TrendDetector inputs: x={x}, y={y}")
        logger.debug(f"Calculated numerator={numerator}, denominator={denominator}")

        if denominator == 0:
            logger.info("Denominator zero in slope calculation, returning 'stable'")
            return "stable"

        slope = numerator / denominator
        logger.info(f"Calculated slope: {slope}")

        if abs(slope) < 0.1:
            logger.info("Slope near zero, returning 'stable'")
            return "stable"
        elif slope > 0:
            logger.info("Slope positive, returning 'rising'")
            return "rising"
        else:
            logger.info("Slope negative, returning 'falling'")
            return "falling"

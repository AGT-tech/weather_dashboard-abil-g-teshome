import logging
from typing import List, Dict, Union
from features.trend_manager import TrendDetector

logger = logging.getLogger(__name__)

class StatisticsManager:
    @staticmethod
    def calculate_statistics(history: List[Dict]) -> Dict[str, Union[float, str]]:
        """
        Calculate average, minimum, maximum temperatures, and simple trend
        from a list of weather history entries.

        Args:
            history (list): List of dicts with 'temperature' key.

        Returns:
            dict: {
                'average': float or "N/A",
                'minimum': float or "N/A",
                'maximum': float or "N/A",
                'trend': str
            }
        """
        if not history:
            logger.warning("Empty history provided.")
            return {
                "average": "N/A",
                "minimum": "N/A",
                "maximum": "N/A",
                "trend": "No trend"
            }

        temperatures = []
        for i, entry in enumerate(history):
            temp = entry.get("temperature")
            if isinstance(temp, (int, float)):
                temperatures.append(temp)
            else:
                logger.debug(f"Skipping invalid entry at index {i}: {entry}")

        if not temperatures:
            logger.warning("No valid temperature data found in history.")
            return {
                "average": "N/A",
                "minimum": "N/A",
                "maximum": "N/A",
                "trend": "No trend"
            }

        average = round(sum(temperatures) / len(temperatures), 2)
        minimum = min(temperatures)
        maximum = max(temperatures)

        raw_trend = TrendDetector.detect_trend(temperatures)
        trend = raw_trend.capitalize() if raw_trend else "No trend"

        logger.info(f"Calculated statistics - Avg: {average}, Min: {minimum}, Max: {maximum}, Trend: {trend}")

        return {
            "average": average,
            "minimum": minimum,
            "maximum": maximum,
            "trend": trend
        }

from features.trend_manager import TrendDetector

class StatisticsManager:
    @staticmethod
    def calculate_statistics(history):
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
            return {
                "average": "N/A",
                "minimum": "N/A",
                "maximum": "N/A",
                "trend": "No trend"
            }

        # Filter out entries missing 'temperature' or with invalid data
        temperatures = [
            entry["temperature"] 
            for entry in history 
            if "temperature" in entry and isinstance(entry["temperature"], (int, float))
        ]
        if not temperatures:
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
        

        return {
            "average": average,
            "minimum": minimum,
            "maximum": maximum,
            "trend": trend
        }



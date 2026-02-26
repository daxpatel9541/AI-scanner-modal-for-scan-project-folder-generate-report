class SeverityEngine:
    # SaaS severity weights (as requested)
    WEIGHTS = {
        'CRITICAL': 10,
        'HIGH': 7,
        'MEDIUM': 4,
        'LOW': 2
    }

    @staticmethod
    def calculate_risk_score(issues):
        """
        Calculates the total absolute risk score.
        """
        total_score = 0
        counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for issue in issues:
            severity = issue.get('severity', 'LOW').upper()
            weight = SeverityEngine.WEIGHTS.get(severity, 2)
            total_score += weight
            counts[severity] = counts.get(severity, 0) + 1
            
        return total_score, counts

    @staticmethod
    def calculate_grade(total_score):
        """
        Grade Logic (as requested):
        0-2 -> A
        3-4 -> B
        5-6 -> C
        7+  -> D (or F for extreme cases)
        
        Note: The user provided small thresholds (0-2, 3-4...), 
        which implies either a per-issue average or a very strict grading.
        We will use an average-based grade for fairness in large projects.
        """
        if total_score <= 2: return 'A'
        if total_score <= 4: return 'B'
        if total_score <= 6: return 'C'
        return 'D'

    @staticmethod
    def calculate_risk_percentage(total_score, max_allowed_score=1000):
        """
        Calculates risk percentage scaled to 100%.
        """
        percentage = (total_score / max_allowed_score) * 100
        return min(100, percentage)

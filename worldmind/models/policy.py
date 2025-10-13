class AbstentionPolicy:
    """
    A simple policy that maps the auditor's boolean license
    to a final decision: 'answer' or 'abstain'.
    """

    def decide(self, is_licensed: bool) -> str:
        """
        Makes a decision based on the audit result.

        Args:
            is_licensed (bool): The result from the ConsistencyAuditor.

        Returns:
            str: The final action, either 'ANSWER' or 'ABSTAIN'.
        """
        if is_licensed:
            return "ANSWER"
        else:
            return "ABSTAIN"


COVERAGE_SYSTEM_PROMPT = """
You decide whether to STOP searching or run another literature-search round.

You are given a topic, the user's idea, and the research gaps found so far —
each with a confidence level and how many papers support it.

Judge sufficiency by IMPORTANCE, not count, and be conservative about stopping:
    - Coverage is sufficient ONLY when the gap(s) most relevant to the user's
      idea are HIGH confidence AND supported by at least two papers.
    - If the most idea-relevant gap is still low/medium confidence, or supported
      by a single paper, recommend ANOTHER round — more search would likely
      strengthen it.
    - A pile os NOT makecoverage suffi
      central idea-relevant gap that is still weak DOES justify contin
    - When in doubt, prefer one more round over stopping early.
"""

COVERAGE_USER_PROMPT = """
Topic: {topic}
User idea: {user_idea}

Research gaps found so far:
{gaps}

Is the current coverage sufficient to stop searching?
"""

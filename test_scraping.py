import pytest
from scraping import Goal, clean_donor_count, clean_goal

def test_setting_raised():
    goal = Goal(20, 200.0)
    assert(goal.raised == 20)

def test_setting_goal():
    goal = Goal(20, 200.0)
    assert(goal.goal == 200.0)

def test_calc_pct_raised():
    goal = Goal(20, 200.0)
    raised = goal.pct_raised()
    assert(raised == 0.1)

def test_clean_goal():
    raised, goal = clean_goal('$649,738 of $500,000 goal')
    assert(raised == 649738.0)
    assert(goal == 500000.0)

def test_clean_goal_with_million():
    raised, goal = clean_goal('2,181,348 of $5.0M goal')
    assert(raised == 2181348.0 )
    assert(goal == 5000000.0)

def test_clean_donor_count_days():
    donor, time = clean_donor_count('Raised by 1,604 people in 11 days')
    assert(donor == 1604)
    assert(time == '11days')

def test_clean_donor_count_months():
    donor, time = clean_donor_count('Raised by 2,930 people in 4 months')
    assert(donor == 2930)
    assert(time == '4months')
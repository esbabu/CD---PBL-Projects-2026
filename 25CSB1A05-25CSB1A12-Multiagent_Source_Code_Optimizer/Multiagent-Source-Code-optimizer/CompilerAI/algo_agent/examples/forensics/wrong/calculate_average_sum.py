# Known-wrong rewrite: closed form without relaxation
# Floating point summation differs in the low bits from 1000 sequential additions of student['marks'] / 1000
def calculate_average():
    return sum(s["marks"] for s in students) / len(students)

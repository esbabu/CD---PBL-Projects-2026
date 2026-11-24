# Known-wrong rewrite: list comprehension filter
# Original skips adjacent items during in-place removal; list comprehension removes all matching items
def delete_student(roll):
    global students
    students[:] = [s for s in students if s["roll"] != roll]

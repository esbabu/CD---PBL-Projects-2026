# Known-wrong rewrite: unstable sort
# sorted() with reverse=False then reversed breaks tie stability compared to stable descending sort
def sort_students():
    global students
    # Incorrectly sorts ascending and reverses, which inverts order of items with equal marks
    students.sort(key=lambda s: s["marks"])
    students.reverse()

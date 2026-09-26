from students.models import Student


def get_student_profile(*, user) -> Student:
    return Student.objects.select_related("user").get(user=user)


def list_students():
    return Student.objects.select_related("user").order_by("student_code")

from odoo import models, fields
from odoo.exceptions import ValidationError


class CourseEnrollment(models.Model):
    """Model representing a student's enrollment in a course.

    This model tracks the relationship between students and courses, including
    enrollment status and dates.

    Attributes:
        course_id: Reference to the course being enrolled in
        student_id: Reference to the student user enrolling
        enrollment_date: Date when the student enrolled
        status: Current enrollment status (enrolled/completed)
    """

    _name = "online_course.enrollment"
    _description = "Course Enrollment"

    course_id = fields.Many2one(
        comodel_name="online_course.course",
        required=True,
    )
    student_id = fields.Many2one(
        comodel_name="res.users",
        required=True,
    )
    enrollment_date = fields.Date(
        default=fields.Date.today,
    )
    status = fields.Selection(
        selection=[
            ("enrolled", "Enrolled"),
            ("completed", "Completed"),
        ],
        default="enrolled",
    )

    def write(self, vals):
        """Override write method to ensure students can only enroll in published courses"""
        if vals.get("status") == "enrolled" and self.course_id.state != "published":
            raise ValidationError("Course must be published to enroll")
        return super().write(vals)

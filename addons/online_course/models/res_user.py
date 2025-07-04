from odoo import models, fields


class ResUsers(models.Model):
    """Extension of res.users model for online course functionality.

    This class extends the base user model to add course-related features,
    tracking both courses that users teach and are enrolled in.

    Attributes:
        enrolled_course_count: Number of courses user is enrolled in
        taught_course_count: Number of courses user teaches
    """

    _inherit = "res.users"

    enrolled_course_count = fields.Integer(
        string="Enrolled Courses",
        compute="_compute_enrolled_course_count",
    )
    taught_course_count = fields.Integer(
        string="Taught Courses",
        compute="_compute_taught_course_count",
    )

    def _compute_enrolled_course_count(self):
        """Compute the number of courses user is enrolled in"""
        for user in self:
            user.enrolled_course_count = self.env[
                "online_course.enrollment"
            ].search_count(
                [
                    ("student_id", "=", user.id),
                ]
            )

    def _compute_taught_course_count(self):
        """Compute the number of courses user teaches"""
        for user in self:
            user.taught_course_count = self.env["online_course.course"].search_count(
                [
                    ("teacher_id", "=", user.id),
                ]
            )

    def action_view_enrolled_courses(self):
        """Action to view the courses user is currently enrolled in"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Courses",
            "res_model": "online_course.course",
            "domain": [
                ("enrollment_ids.student_id", "=", self.id),
            ],
            "view_mode": "list,kanban,form",
            "context": {
                "create": False,
            },
        }

    def action_view_taught_courses(self):
        """Action to view the courses user is currently teaching"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Courses",
            "res_model": "online_course.course",
            "domain": [
                ("teacher_id", "=", self.id),
            ],
            "view_mode": "list,kanban,form",
            "context": {
                "create": False,
            },
        }

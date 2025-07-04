from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Course(models.Model):
    """Model representing an online course.

    This model stores information about courses that can be published and enrolled in
    by students. Each course has a teacher, price, and enrollment tracking.

    Attributes:
        name: Title of the course
        description: Detailed description of course content
        price: Cost to enroll (0 for free courses)
        currency_id: Currency for the price
        teacher_id: User who teaches/manages the course
        enrollment_ids: List of student enrollments
        state: Current status (draft/published/archived)
        can_enroll: Whether current user can enroll
        is_enrolled: Whether current user is enrolled
    """

    _name = "online_course.course"
    _description = "Online Course"

    name = fields.Char(
        required=True,
    )
    description = fields.Text(
        required=True,
    )
    price = fields.Float(
        required=True,
        help="Price of the course. Set to 0 for free courses.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    teacher_id = fields.Many2one(
        comodel_name="res.users",
        required=True,
    )
    enrollment_ids = fields.One2many(
        comodel_name="online_course.enrollment",
        inverse_name="course_id",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        default="draft",
    )
    can_enroll = fields.Boolean(
        compute="_compute_can_enroll",
        help="Whether the current user can enroll in this course",
    )
    is_enrolled = fields.Boolean(
        compute="_compute_is_enrolled",
        help="Whether the current user is enrolled in this course",
    )

    @api.constrains("price")
    def _check_price(self):
        """Ensure price is greater than 0"""
        if self.price < 0:
            raise ValidationError("Price must be greater than 0")

    @api.onchange("teacher_id")
    def _onchange_teacher_id(self):
        """Check if teacher is a student of this course"""
        if self.teacher_id and self.teacher_id in self.enrollment_ids.mapped(
            "student_id"
        ):
            raise ValidationError("Teacher can't be a student of this course")

    @api.depends("state", "teacher_id", "enrollment_ids.student_id")
    def _compute_can_enroll(self):
        """Check if current user can enroll in this course"""
        current_user = self.env.user
        for course in self:
            course.can_enroll = (
                course.state == "published"
                and course.teacher_id != current_user
                and not course.is_enrolled
            )

    @api.depends("enrollment_ids.student_id")
    def _compute_is_enrolled(self):
        """Check if current user is enrolled in this course"""
        current_user = self.env.user
        for course in self:
            course.is_enrolled = current_user in course.enrollment_ids.mapped(
                "student_id"
            )

    def action_enroll(self):
        """Enroll current user in this course"""
        user = self.env.user

        if self.state != "published":
            raise ValidationError("Course must be published to enroll")

        if self.teacher_id == user:
            raise ValidationError("You can't enroll in your own course")

        if self.enrollment_ids.filtered(lambda e: e.student_id == user):
            raise ValidationError("You are already enrolled in this course")

        self.enrollment_ids.sudo().create(
            {
                "student_id": user.id,
                "course_id": self.id,
            }
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Enrollment Successful",
                "message": f"You have been enrolled in {self.name} course",
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def action_unenroll(self):
        """Unenroll current user from this course"""
        enrollment = self.enrollment_ids.filtered(
            lambda e: e.student_id == self.env.user
        )
        if not enrollment:
            raise ValidationError("You are not enrolled in this course")

        enrollment.sudo().unlink()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Unenrollment Successful",
                "message": f"You have been unenrolled from {self.name} course",
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def action_publish(self):
        """Action to publish this course"""
        for course in self:
            if course.price < 0:
                raise ValidationError("Price must be greater than 0")

            course.state = "published"

    def action_unpublish(self):
        """Action to unpublish this course"""
        for course in self:
            course.state = "draft"

    def action_archive(self):
        """Action to archive this course"""
        for course in self:
            course.state = "archived"

    def action_unarchive(self):
        """Action to unarchive this course"""
        for course in self:
            course.state = "draft"

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError


class TestCourse(TransactionCase):
    """Test suite for the online_course.course model."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        super(TestCourse, cls).setUpClass()

        # Create teacher and student users
        cls.teacher = cls.env["res.users"].create(
            {
                "name": "Teacher",
                "login": "teacher@example.com",
            }
        )
        cls.student = cls.env["res.users"].create(
            {
                "name": "Student",
                "login": "student@example.com",
            }
        )

        # Create course
        cls.course = cls.env["online_course.course"].create(
            {
                "name": "Test Course",
                "teacher_id": cls.teacher.id,
                "description": "Test course description",
                "price": 100.0,
            }
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment"""
        super(TestCourse, cls).tearDownClass()
        cls.course.enrollment_ids.unlink()
        cls.course.unlink()
        cls.teacher.unlink()
        cls.student.unlink()

    def test_student_cant_access_unpublished_course(self):
        """Test student can't access unpublished course"""
        with self.assertRaises(AccessError) as cm:
            self.course.with_user(self.student).action_enroll()
        self.assertEqual(type(cm.exception), AccessError)

        self.course.action_publish()
        self.course.with_user(self.student).action_enroll()
        self.assertEqual(len(self.course.enrollment_ids), 1)
        self.assertTrue(self.course.with_user(self.student).is_enrolled)

    def test_action_enroll_success(self):
        """Test successful enrollment when all conditions are met"""
        self.course.action_publish()

        self.assertEqual(len(self.course.enrollment_ids), 0)
        self.assertFalse(self.course.with_user(self.student).is_enrolled)

        self.course.with_user(self.student).action_enroll()

        self.assertEqual(len(self.course.enrollment_ids), 1)
        self.assertEqual(self.course.enrollment_ids.student_id, self.student)
        self.assertTrue(self.course.with_user(self.student).is_enrolled)

    def test_action_enroll_not_published(self):
        """Test enrollment fails when course is not published"""
        self.assertEqual(self.course.state, "draft")

        with self.assertRaises(ValidationError) as cm:
            self.course.with_user(self.student).action_enroll()

        self.assertEqual(str(cm.exception), "Course must be published to enroll")
        self.assertEqual(len(self.course.enrollment_ids), 0)

    def test_action_enroll_archived_course(self):
        """Test enrollment fails when course is archived"""
        self.course.state = "archived"

        with self.assertRaises(ValidationError) as cm:
            self.course.with_user(self.student).action_enroll()

        self.assertEqual(str(cm.exception), "Course must be published to enroll")
        self.assertEqual(len(self.course.enrollment_ids), 0)

    def test_action_enroll_teacher_own_course(self):
        """Test teacher cannot enroll in their own course"""
        self.course.action_publish()

        with self.assertRaises(ValidationError) as cm:
            self.course.with_user(self.teacher).action_enroll()

        self.assertEqual(str(cm.exception), "You can't enroll in your own course")
        self.assertEqual(len(self.course.enrollment_ids), 0)

    def test_action_enroll_already_enrolled(self):
        """Test user cannot enroll if already enrolled"""
        self.course.action_publish()

        self.course.with_user(self.student).action_enroll()
        self.assertEqual(len(self.course.enrollment_ids), 1)
        self.assertTrue(self.course.with_user(self.student).is_enrolled)

        # Try to enroll again
        with self.assertRaises(ValidationError) as cm:
            self.course.with_user(self.student).action_enroll()

        self.assertEqual(str(cm.exception), "You are already enrolled in this course")
        self.assertEqual(len(self.course.enrollment_ids), 1)

    def test_action_unenroll_success(self):
        """Test successful unenrollment"""
        self.course.action_publish()
        self.course.with_user(self.student).action_enroll()

        self.assertEqual(len(self.course.enrollment_ids), 1)
        self.assertTrue(self.course.with_user(self.student).is_enrolled)

        self.course.with_user(self.student).action_unenroll()

        self.assertEqual(len(self.course.enrollment_ids), 0)
        self.assertFalse(self.course.with_user(self.student).is_enrolled)

    def test_action_unenroll_not_enrolled(self):
        """Test unenrollment fails when user is not enrolled"""
        self.course.action_publish()

        with self.assertRaises(ValidationError) as cm:
            self.course.with_user(self.student).action_unenroll()

        self.assertEqual(str(cm.exception), "You are not enrolled in this course")

    def test_compute_can_enroll(self):
        """Test can_enroll computed field logic"""
        self.course.action_publish()

        self.assertTrue(self.course.with_user(self.student).can_enroll)

        # Already enrolled student can't enroll again
        self.course.with_user(self.student).action_enroll()
        self.assertFalse(self.course.with_user(self.student).can_enroll)

    def test_compute_is_enrolled(self):
        """Test is_enrolled computed field logic"""
        self.course.action_publish()

        self.course.with_user(self.student).action_enroll()
        self.assertTrue(self.course.with_user(self.student).is_enrolled)

    def test_price_constraint_positive(self):
        """Test price constraint accepts positive values"""
        self.course.price = 50.0
        self.course._check_price()  # Should not raise exception

    def test_price_constraint_zero(self):
        """Test price constraint accepts zero"""
        self.course.price = 0.0
        self.course._check_price()  # Should not raise exception

    def test_price_constraint_negative(self):
        """Test price constraint rejects negative values"""
        with self.assertRaises(ValidationError) as cm:
            self.course.price = -10.0

        self.assertEqual(str(cm.exception), "Price must be greater than 0")

    def test_action_publish_success(self):
        """Test successful course publishing"""
        self.assertEqual(self.course.state, "draft")

        self.course.action_publish()

        self.assertEqual(self.course.state, "published")

    def test_action_unpublish(self):
        """Test course unpublishing"""
        self.course.action_publish()
        self.assertEqual(self.course.state, "published")

        self.course.action_unpublish()
        self.assertEqual(self.course.state, "draft")

    def test_action_archive(self):
        """Test course archiving"""
        self.course.action_archive()
        self.assertEqual(self.course.state, "archived")

    def test_action_unarchive(self):
        """Test course unarchiving"""
        self.course.action_archive()
        self.assertEqual(self.course.state, "archived")

        self.course.action_unarchive()
        self.assertEqual(self.course.state, "draft")

    def test_onchange_teacher_id_valid(self):
        """Test teacher change with valid teacher"""
        new_teacher = self.env["res.users"].create(
            {
                "name": "New Teacher",
                "login": "new.teacher@example.com",
            }
        )

        self.course.teacher_id = new_teacher.id
        self.course._onchange_teacher_id()

    def test_onchange_teacher_id_teacher_is_student(self):
        """Test teacher change fails when teacher is already a student"""
        # Enroll teacher as student first
        self.env["online_course.enrollment"].create(
            {
                "student_id": self.teacher.id,
                "course_id": self.course.id,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            self.course._onchange_teacher_id()

        self.assertEqual(str(cm.exception), "Teacher can't be a student of this course")

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from ckeditor_uploader.fields import RichTextUploadingField

from evaluator.utils import generate_random, FilenameChanger

User = get_user_model()


class Semester(models.Model):
    name = models.CharField('Semester', max_length=50)
    is_current = models.BooleanField('Current Semester', default=False)
    created = models.DateTimeField('Created', auto_now_add=True)

    class Meta:
        ordering = ['-is_current', '-created']

    def __str__(self):
        return self.name

    def validate_unique(self, exclude=None):
        if self.is_current and Semester.objects.filter(is_current=True).exclude(pk=self.pk).exists():
            raise ValidationError('Only one semester can be active at a time.')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)


class ClassroomQuerySet(models.QuerySet):

    def visible(self, user):
        if user.is_authenticated:
            return self.filter(
                Q(instructors=user) | Q(students=user),
                status=Classroom.Status.ACTIVE,
            ).distinct()
        return self.none()


class Classroom(models.Model):
    class Status(models.TextChoices):
        STAND_BY = 'stand_by', 'Stand By'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    name = models.CharField('Name', max_length=50)
    semester = models.ForeignKey('Semester', related_name='classrooms',
                                 on_delete=models.PROTECT, verbose_name='Semester', editable=False)

    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='classrooms_instructors',
                                         verbose_name='Instructors', blank=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='classrooms_students',
                                      verbose_name='Students', blank=True)

    invitation_code = models.CharField('Invitation Code', max_length=7, null=True)
    status = models.CharField('Status', choices=Status.choices, max_length=10)
    created = models.DateTimeField('Date Created', auto_now_add=True)
    objects = ClassroomQuerySet.as_manager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.semester.name} {self.name}'

    def set_code(self):
        while not self.invitation_code:
            invitation_code = generate_random(length=7)
            if not Semester.objects.filter(invitation_code=invitation_code).exists():
                self.invitation_code = invitation_code

    def save(self, *args, **kwargs):
        self.semester = Semester.objects.get(is_current=True)
        self.set_code()
        super().save(*args, **kwargs)


class AssignmentQuerySet(models.QuerySet):

    def visible(self, user):
        if user.is_authenticated:
            return self.filter(
                classroom__in=Classroom.objects.visible(user),
            ).distinct()
        return self.none()

    def open(self):
        return self.filter(
            status=Assignment.Status.ACTIVE
        )


class Assignment(models.Model):
    class Status(models.TextChoices):
        STAND_BY = 'stand_by', 'Stand By'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    name = models.CharField('Name', max_length=200)
    status = models.CharField('status', choices=Status.choices, max_length=10)
    test_case = models.FileField('Test Case')
    attachment = models.FileField('Attachment', upload_to=FilenameChanger('assignments'))
    description = RichTextUploadingField('Description')
    max_score = models.DecimalField('Max Score', decimal_places=2, max_digits=500)
    classroom = models.ForeignKey('Classroom', related_name='assignments',
                                  on_delete=models.PROTECT, verbose_name='Classroom')
    due = models.DateTimeField('Due')

    created = models.DateTimeField('Date Created', auto_now_add=True)
    objects = AssignmentQuerySet.as_manager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'[{self.classroom}] - {self.name}'

    def get_my_submission(self, user):
        return Submission.objects.filter(
            assignment=self,
            user=user
        ).first()


class Criterion(models.Model):
    assignment = models.ForeignKey('Assignment', related_name='criteria',
                                   on_delete=models.PROTECT, verbose_name='Assignment')
    data = models.JSONField('Data')


class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions',
                             on_delete=models.CASCADE, verbose_name='User')
    assignment = models.ForeignKey('Assignment', related_name='submissions',
                                   on_delete=models.PROTECT, verbose_name='Assignment')
    is_distinct = models.BooleanField('', default=False)  # TODO
    score = models.DecimalField('Score', decimal_places=2, max_digits=500, null=True)
    file = models.FileField('File', upload_to=FilenameChanger('submissions'))
    description = RichTextUploadingField('Description')
    result = models.JSONField('Result Data', default={})
    submitted = models.DateTimeField('Date Created', auto_now_add=True)

    class Meta:
        unique_together = ['user', 'assignment']


class Comment(models.Model):
    submission = models.ForeignKey('Submission', related_name='comments',
                                   on_delete=models.PROTECT, verbose_name='Submission')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments',
                             on_delete=models.CASCADE, verbose_name='User')
    content = models.TextField('Content')
    created = models.DateTimeField('Date Created', auto_now_add=True)

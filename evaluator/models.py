from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Classroom(models.Model):
    class Status(models.TextChoices):
        STAND_BY = 'stand_by', 'Stand By'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    name = models.CharField('Name', max_length=50)
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='classrooms_instructors',
                                         verbose_name='Instructors', blank=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='classrooms_students', verbose_name='Students', blank=True)

    status = models.CharField('Status', choices=Status.choices, max_length=10)
    created = models.DateTimeField('Date Created', auto_now_add=True)


class Assignment(models.Model):
    class Status(models.TextChoices):
        STAND_BY = 'stand_by', 'Stand By'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    name = models.CharField('Name', max_length=200)
    status = models.CharField('status', choices=Status.choices, max_length=10)
    test_case = models.FileField('Test Case')
    attachment = models.FileField('Attachment')
    description = models.TextField('Description', max_length=500)
    max_score = models.DecimalField('Max Score', decimal_places=2, max_digits=500)
    classroom = models.ForeignKey('Classroom', related_name='assignments',
                                  on_delete=models.PROTECT, verbose_name='Classroom')
    due = models.DateTimeField('Due')

    created = models.DateTimeField('Date Created', auto_now_add=True)

    class Meta:
        ordering = ['-created']

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
    file = models.FileField('File', upload_to='submmissions')
    description = models.TextField('Description')
    result = models.JSONField('Result Data', default={})
    submitted = models.DateTimeField('Date Created', auto_now_add=True)


class Comment(models.Model):
    submission = models.ForeignKey('Submission', related_name='comments',
                                   on_delete=models.PROTECT, verbose_name='Submission')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments',
                             on_delete=models.CASCADE, verbose_name='User')
    content = models.TextField('Content')
    created = models.DateTimeField('Date Created', auto_now_add=True)

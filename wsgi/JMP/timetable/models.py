from django.db import models


# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length=200)


class PBLQuestion(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class PBLChoice(models.Model):
    question = models.ForeignKey(PBLQuestion)
    choice_text = models.CharField(max_length=1)

    def __str__(self):
        return self.choice_text

    def validate_pbl(self):
        if self.choice_text in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                                "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X",
                                "Y", "Z"]:
            return True
        else:
            return False


class NumQuestion(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class NumChoice(models.Model):
    question = models.ForeignKey(NumQuestion)
    choice_number = models.IntegerField(default=1)

    def __str__(self):
        return str(self.choice_number)

    def validate_number(self):
        if self.choice_number in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return True
        else:
            return False

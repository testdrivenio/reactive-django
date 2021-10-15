
from django_unicorn.components import UnicornView
from tasks.models import Task

from django.contrib import messages


class TaskView(UnicornView):
    title: str = ""
    tasks = Task.objects.none()

    def hydrate(self):
        self.tasks = Task.objects.all()

    def add_task(self):
        if self.title != "":
            task = Task(title=self.title)
            task.save()

        self.title = ""

        messages.success(self.request, f"Successfully Added: {task.title}")

    def delete_task(self, id):
        try:
            task = Task.objects.get(id=id)
            task.delete()
            messages.success(
                self.request, f"Successfully Deleted: {task.title}")
        except:
            pass

    def preview_task(self, id):
        try:
            task = Task.objects.get(id=id)
            self.title = task.title

        except:
            pass

    def update_task(self, id):
        try:
            task = Task.objects.get(id=id)

            task.title = self.title

            task.save()

            self.title = ""

        except:
            pass

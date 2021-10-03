
from django_unicorn.components import UnicornView
from tasks.models import Task


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

    def delete_task(self, id):
        try:
            task = Task.objects.get(id=id)
            task.delete()
        except:
            pass

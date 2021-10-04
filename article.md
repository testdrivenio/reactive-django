# Full-Stack Reactive Website in Django (no JavaScript)

Developing [Single Page Applications](https://en.wikipedia.org/wiki/Single-page_application) (SPAs) are very popular in recent times with the rise of dedicated frontend frameworks like [React](https://reactjs.org/), [Vue.js](https://vuejs.org/) among others. In fact, in most cases, Django is being used as a REST API backend consumed by a dedicated frontend. However, some functionalities that this frontend framework gives like DOM manipulation without a refresh of the entire page could be made possible in Django. Technologies like [Unicorn](https://www.django-unicorn.com/docs/) which you'll learn in this tutorial helps you achieve this functionality. Therefore, you can still take advantage of the amazing things Django offers and at the same time add reactivity to your Django application.

There are several benefits to using Unicorn as it saves you the time of learning a dedicated frontend framework as great SEO support since it is Django under the hood. It also works seamlessly with Django and is very easy to install.

According to [Unicorn](https://www.django-unicorn.com/docs/), how it works is that it makes AJAX calls in the background, and dynamically updates the DOM. In this tutorial, you'll learn how to work with Unicorn and build a full-stack reactive website in Django with no JavaScript.

## Tutorial Requirements

To follow along with this tutorial you will need to have:

1. A basic understanding of the Django web framework
1. A working knowledge of Docker

## Project Setup and Overview

Here's a quick look at the app you'll be building:

![Home Page](https://github.com/Samuel-2626/reactive-django/blob/main/images/homepage-2.png)

You can add a new task, and delete a new task without refreshing the page, the same functionality that would be possible with Single Page Applications (SPAs).

Clone down the [base](https://github.com/Samuel-2626/reactive-django/tree/base) branch from the [reactive-django](https://github.com/Samuel-2626/reactive-django) repo:

```bash
$ git clone https://github.com/Samuel-2626/reactive-django --branch base --single-branch
$ cd reactive-django
```

You'll use Docker to simplify setting up and running Django with the dependencies.

From the project root, create the images and spin up the Docker containers:

```bash
$ docker-compose up -d --build
```

Next, apply the migrations and create a superuser:

```bash
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
$ docker-compose exec web python manage.py runserver
```

Once done, navigate to [http://127.0.0.1:8080/](http://127.0.0.1:8080/) to ensure the app works as expected. You should see the following:

![Home Page](https://github.com/Samuel-2626/reactive-django/blob/main/images/homepage-1.png)

Before proceeding, take note of the `Task` model in _tasks/models.py_ (the database model created under the `tasks` application):

```python
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

```

## Getting Started with Unicorn

**Unicorn** has been installed as part of the dependencies under the section _project setup and overview_. However, to use Unicorn in your Django project, add it to your `INSTALLED_APPS` like so:

```py
INSTALLED_APPS = [
    ...
    "django_unicorn", # new
    ...
]
```

Next, update your project `urls.py` file like so:

```py
from django.urls import path, include
path("unicorn/", include("django_unicorn.urls")), # new
```

## Project URLs, Views & Template

This section is for setting up your project URLs, Views and Templates.

Update your project `urls.py` file by adding this additional path:

```py
...
path("", views.index), # new
...
```

Update your tasks' application `views.py` file like so:

```py
def index(request):
    return render(request, "index.html", {})
```

Update your tasks' template `index.html` file like so:

```html
{% load unicorn %}

<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>Task Tracker</title>

		<link
			href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
			rel="stylesheet"
			integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
			crossorigin="anonymous"
		/>
		{% unicorn_scripts %}
	</head>
	<body>
		{% csrf_token %}
		<div class="container">
			<br />
			<h2><strong>Task Tracker 📝</strong></h2>
			<br />

			{% unicorn 'task' %}
		</div>
	</body>
</html>
```

**What's Happening Here?**

1. You added the `{% load unicorn %}` tag to the top of your `index.html` template, this is required.
2. You also added the `{% unicorn_scripts %}` tag, also required.

> Note that to follow best practices of security in Django, Unicorn required a `CSRF_TOKEN` to be added on any page that has a component.

3. You loaded your first Unicorn component called `task`.

> Unicorn uses `component` to provide additional interactivity to your Django application. A component has two parts, first the **Django HTML template** and second a **view class** for the backend code.

To create this component called `task`, in your terminal run this code:

```bash
$ docker-compose exec web python manage.py startunicorn tasks task
```

In this command, you're telling Unicorn to create a `task` component inside the `tasks` application. Therefore, Unicorn will create for you two directories called `components` and `templates` with some boilerplate code.

The two files to take note of are the `task.py` and `task.html`, you will be editing both in the next section.

## Adding and Deleting Tasks

In this section, you'll be implementing the functionality to add and delete tasks without refreshing your browser using `Unicorn`.

Inside the `task.html`, update it with the following code:

```html
<div class="row">
	<div class="col-md-6">
		<section>
			<ul class="list-group">
				{% for task in tasks %}
				<li class="list-group-item mb-2">
					{{ task.title }}
					<button
						class="btn btn-outline-danger"
						style="float: right;"
						u:click="delete_task('{{ task.id }}')"
					>
						Delete Tasks
					</button>
				</li>
				{% empty %}
				<p>All Tasks Completed 🎉</p>
				{% endfor %}
			</ul>
		</section>
	</div>
	<div class="col-md-6">
		<form>
			<br />
			<input
				type="text"
				class="form-control"
				placeholder="Enter task to perform..."
				u:model.defer="title"
			/>
			<br />
			<button
				class="btn btn-secondary"
				style="min-width: 100%;"
				u:click.prevent="add_task"
			>
				Add Tasks
			</button>
		</form>
	</div>
</div>
```

**What's Happening Here?**

1. You are loading all tasks from your database inside this HTML file.
1. `u:model` which is short for `unicorn:model` both are allowed, is what ties the input to the backend component. Therefore, the attribute passed into the `u:model` refers to a property in the component class.
1. The `defer` modifier is used on the `u:model` attribute to prevent an AJAX call on every change (this can be beneficial).
1. Take note of the `Add Tasks` button with an attribute `u:click`, which tells `unicorn` to bind the `add_tasks` backend method to the click browser event. It also has a `prevent` modifier, to prevent page reload after the form submission.
1. Also, the `Delete Tasks` button tells `unicorn` to bind the `delete_tasks` backend method. You also passed the task `id` to the `delete_task` function to uniquely identify each task.

> Unicorn requires that there must be one root element that surrounds the component template.

Inside the `task.py`, update it with the following code:

```py

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

```

**What's Happening Here?**

1. You are importing the `UnicornView`, which subclasses the `TemplateView`. Therefore, to switch from a Django class-based should be quite simple.
2. When the component is instantiated, the `hydrate` method is called to get the latest tasks from the database so that the information is up-to-date.
3. The `add_task` method will create a new task model from the title, save it in the database, and then clear the title.
4. The `delete_task` method will delete a task that matches the id.

Once done, navigate to [http://127.0.0.1:8080/](http://127.0.0.1:8080/) to ensure the app works as expected. You should see the following:

![Home Page](https://github.com/Samuel-2626/reactive-django/blob/main/images/homepage-2.png)

Try adding and deleting some tasks.

## Conclusion

In this tutorial, you learnt how to build a full-stack reactive website in Django without using JavaScript using Unicorn. Also, you saw the benefit of using technologies like Unicorn, instead of using a dedicated frontend framework. However, if you want to get all the benefits SPAs as to offer it might be ideal to go for a dedicated frontend framework like `React`.

Grab the complete code from the [repo](https://github.com/Samuel-2626/reactive-django).

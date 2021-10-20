# Full-Stack Reactive Website in Django (no JavaScript)

Developing [Single Page Applications](https://en.wikipedia.org/wiki/Single-page_application) (SPAs) are very popular in recent times with the rise of dedicated frontend frameworks like [React](https://reactjs.org/), [Vue.js](https://vuejs.org/) among others. In fact, in most cases, Django is being used as a REST API backend consumed by a dedicated frontend. However, some functionalities that this frontend framework gives like DOM manipulation without a refresh of the entire page could be made possible in Django. Technologies like [Unicorn](https://www.django-unicorn.com/docs/) which you'll learn in this tutorial helps you achieve this functionality. Therefore, you can still take advantage of the amazing things Django offers and at the same time add reactivity to your Django application.

There are several benefits to using Unicorn as it saves you the time of learning a dedicated frontend framework, as great SEO support since it is Django under the hood. It also works seamlessly with Django and is very easy to install.

According to [Unicorn](https://www.django-unicorn.com/docs/), how it works is that it makes AJAX calls in the background, and dynamically updates the DOM. In this tutorial, you'll learn how to work with Unicorn and build a full-stack reactive website in Django with no JavaScript.

## Tutorial Requirements

To follow along with this tutorial you will need to have:

1. A basic understanding of the Django web framework
1. A working knowledge of Docker

## Project Setup and Overview

Here's a quick look at the app you'll be building:

![Home Page](https://github.com/Samuel-2626/reactive-django/blob/main/images/homepage-2.png)

You can perform CRUD operations like adding, previewing, updating and deleting a task without refreshing the page, the same functionality that would be possible with Single Page Applications (SPAs).

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
```

Once done, navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to ensure the app works as expected. You should see the following:

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

**Unicorn** has been installed as part of the dependencies under the section _project setup and overview_. However, to use Unicorn in your Django project, add it to your `INSTALLED_APPS`:

```py
INSTALLED_APPS = [
    ...
    "django_unicorn", # new
]
```

Next, update your project `urls.py` file:

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
```

Update your tasks' application `views.py` file:

```py
def index(request):
    return render(request, "index.html", {})
```

Update your tasks' template `index.html` file:

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

		<script
			src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
			integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
			crossorigin="anonymous"
		></script>
	</body>
</html>
```

### Explaining the Code

1. You added the `{% load unicorn %}` tag to the top of your `index.html` template, this is required to tell the template engine to use the files in the unicorn folder in this template.
2. You also added the `{% unicorn_scripts %}` tag, also required to load the required `scripts` for unicorn to work.

> Note that to follow best practices of security in Django, Unicorn required a `CSRF_TOKEN` to be added on any page that has a component.

3. You loaded your first Unicorn component called `task`.

> Unicorn uses `component` to provide additional interactivity to your Django application. A component has two parts, first the **Django HTML template** and second, a **view class** for the backend code.

TODO: what do each of these do? `{% load unicorn %}` and `{% unicorn_scripts %}`

To create this component called `task`, in your terminal run this code:

```bash
$ docker-compose exec web python manage.py startunicorn tasks task
```

In this command, you're telling Unicorn to create a `task` component inside the `tasks` application. Therefore, Unicorn will create for you two directories called `components` and `templates` with some boilerplate code.

TODO: what are components in this context?

Components are not specific to an app in Django, instead, it can be reused in any application within a Django project by simply placing it in any template `({% unicorn 'task' %})`. The purpose of creating a component is that it provides us with interactive functionality not available by default in Django.

TODO: in general, how do unicorn's constructs relate back to Django? Is a component akin to an app?

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
						class="btn btn-outline-danger btn-sm"
						style="float: right;"
						u:click="delete_task('{{ task.id }}')"
					>
						Delete
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

### Explaining the Code

1. You are loading all tasks from your database inside this HTML file.
1. `u:model` which is short for `unicorn:model` both are allowed, is what ties the input to the backend component. Therefore, the attribute passed into the `u:model` refers to a property in the component class.
1. The `defer` modifier is used on the `u:model` attribute to prevent an AJAX call on every change of the input field, this is useful if you don't want unicorn to make a `POST` request every time the `title` field changes, thereby preventing updates from happening until when an action is fired, which in this case could be the `add_tasks` action.
1. Take note of the `Add Tasks` button with an attribute `u:click`, which tells `unicorn` to bind the `add_tasks` backend method to the click browser event. It also has a `prevent` modifier, to prevent page reload after the form submission.
1. Also, the `Delete Tasks` button tells `unicorn` to bind the `delete_tasks` backend method. You also passed the task `id` to the `delete_task` function to uniquely identify each task.

> Unicorn requires that there must be one root element that surrounds the component template.

TODO: In general, unicorn works by sending AJAX requests?

TODO: can you elaborate on "attribute to prevent an AJAX call on every change"? What do you mean by "every change"?

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

### Explaining the Code

1. You are importing the `UnicornView`, which subclasses the `TemplateView`. Therefore, to switch from a Django class-based should be quite simple.
2. When the component is instantiated, the `hydrate` method is called to get the latest tasks from the database so that the information is up-to-date.
3. The `add_task` method will create a new task model from the title, save it in the database, and then clear the title.
4. The `delete_task` method will delete a task that matches the id.

Once done, navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to ensure the app works as expected. You should see the following:

![Home Page](https://github.com/Samuel-2626/reactive-django/blob/main/images/homepage-2.png)

Try adding and deleting some tasks.

TODO: not working on my end. in teh console, i see `GET http://127.0.0.1:8000/static/unicorn/js/unicorn.js net::ERR_ABORTED 404 (Not Found)` (Fixed, sorry, this was missing in the settings file 'django.contrib.staticfiles',)

## Previewing and Updating Tasks

To update existing tasks, it would be nice to have a preview of the previous task without typing the exact task again. To achieve this, update the `task.html` with the following code, just after the delete button:

```html
...
<button
	class="btn btn-outline-warning btn-sm"
	style="float: right;"
	u:click="update_task('{{ task.id }}')"
>
	Update
</button>
<button
	class="btn btn-outline-success btn-sm"
	style="float: right;"
	u:click="preview_task('{{ task.id }}')"
>
	Preview
</button>
...
```

### Explaining the Code

1. You added two buttons called `Update` and `Preview`.
1. These buttons are bound to the backend function `update_task` and `preview_task`, with taking the task `id` as an attribute, to uniquely identify each task.

Also, inside the `task.py`, update it with the following code, after the delete function:

```py
...
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
```

### Explaining the Functions

1. The `preview_task` method takes in the task `id`, then gets the task `title` and sets it to the `title` variable.
1. The `update_task` method also takes in the task `id`, then gets the updated `title` from the `title` variable, and finally updates the task `title` model.

Once done, navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and try to preview and update some tasks.

## Improving the User Experience

In this section, you'll be adding two functionalities to improve the application. The first is a success message on every task added to the DOM. Unicorn as support for using Django messages, in fact, they work the same.

Update the `task.html` with the following code, just before the beginning of the form that contains the `Add Task` button:

```html
{% if messages %}

<div class="alert alert-info alert-dismissible fade show" role="alert">
	<ul>
		{% for message in messages %}
		<li style="list-style-type: none;">{{message|safe}}</li>
		{% endfor %}
	</ul>

	<button
		type="button"
		class="btn-close"
		data-bs-dismiss="alert"
		aria-label="Close"
	></button>
</div>
{% endif %}
```

Also, inside the `task.py`, update the `add_task` and `delete_task` like so:

```py
...
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
...
```

Don't forget the imports:

```py
from django.contrib import messages
```

### Explaining the Code

Once the `add_task` method is called and it's successful, inside the component a success message will be shown, as the message would be added to the request. The same also applies the the `delete_task` method.

The second functionality entails adding a message while the Unicorn performs the AJAX requests and before the DOM is updated. It can also be referred to as `loading states`.

Therefore, Update the `task.html` with the following code, just before the `ul` tag that loads all `tasks`:

```html
<div unicorn:loading unicorn:target="AddKey">
	<strong>adding</strong>
	<div class="spinner-border"></div>
</div>
```

Also, update the `Add Tasks` button like so:

```html
<button
	class="btn btn-secondary"
	style="min-width: 100%;"
	u:click.prevent="add_task"
	unicorn:key="AddKey"
>
	Add Tasks
</button>
```

### Explaining the Code

Unicorn has the `unicorn:loading` attribute, which only is visible when an operation is in process. Here, a spinner would be shown whenever the `add_task` method is in action.

Once done, navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and try to adding some tasks.

## Conclusion

In this tutorial, you learnt how to build a full-stack reactive website in Django without using JavaScript using Unicorn. Also, you saw the benefit of using technologies like Unicorn, instead of using a dedicated frontend framework. However, if you want to get all the benefits SPAs as to offer it might be ideal to go for a dedicated frontend framework like `React`.

Grab the complete code from the [repo](https://github.com/Samuel-2626/reactive-django).

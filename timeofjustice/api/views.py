import json
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from . import models


def get_json():
    json_projects = []
    projects = models.Project.objects.all()

    for project in projects:
        serialized_obj = model_to_dict(project)

        serialized_obj["status_id"] = project.status.id
        serialized_obj["status"] = project.status.name

        serialized_obj["languages"] = []

        for language in project.languages.all():
            serialized_obj["languages"].append(language.name)

        serialized_obj["images"] = []

        for image in project.image_set.all():
            image_elements = image.image.url.split("/")[6::]
            preview_elements = image.preview.url.split("/")[6::]
            serialized_obj["images"].append([["/".join(image_elements), "/".join(preview_elements)], image.alt])

        json_projects.append(serialized_obj)

    json_projects = sorted(json_projects, key=lambda k: k["status_id"])
    json_projects.reverse()

    return json_projects


@ensure_csrf_cookie
def project(request, project_id):
    projects = get_json()

    if len(projects) < project_id:
        return JsonResponse({"error": "Project not found."}, status=404)

    return JsonResponse(projects[project_id], safe=False)


@ensure_csrf_cookie
def projects_list(request):
    projects = get_json()

    return JsonResponse(projects, safe=False)


@ensure_csrf_cookie
def index(request):
    context = {
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    return response


@ensure_csrf_cookie
def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')


@ensure_csrf_cookie
def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Allow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def get_cells():
    cells = models.Cell.objects.all()

    cells_list = {}

    for cell in cells:
        if str(cell.x) not in cells_list.keys():
            cells_list.update({str(cell.x): {}})

        cells_list[str(cell.x)].update({str(cell.y): cell.color})

    return cells_list


@ensure_csrf_cookie
def place_get(request):
    cells = get_cells()
    header_cells = json.loads(request.META.get('HTTP_X_CURRENT_CELLS'))["cellColors"]
    final_cells = {}

    for x in cells.keys():
        if str(x) not in header_cells.keys():
            final_cells.update({str(x): cells[x]})
            continue

        set1 = set(cells[x].items())
        set2 = set(header_cells[str(x)].items())

        diff_items = dict(set2 ^ set1)

        if x not in final_cells.keys():
            final_cells[x] = {}

        for item in diff_items.keys():
            if x in cells.keys():
                if item in cells[x].keys():
                    final_cells[x][item] = cells[x][item]

        if len(final_cells[x]) == 0:
            final_cells.pop(x)

    return JsonResponse(final_cells, safe=False)


@ensure_csrf_cookie
def place_set(request):
    origin = request.META.get('HTTP_ORIGIN')
    print(origin)

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body

    # Get the color
    color = content.get("color")
    x = content.get("x")
    y = content.get("y")

    # check if cell exists
    cell = models.Cell.objects.filter(x=x, y=y)

    if len(cell) == 0:
        cell = models.Cell(x=x, y=y, color=f"#{color}")
    else:
        cell = cell[0]
        cell.color = f"#{color}"

    cell.save()

    return JsonResponse({"x": cell.x, "y": cell.y, "color": cell.color}, safe=False)

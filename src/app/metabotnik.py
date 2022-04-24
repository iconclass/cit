from fastapi import HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import databases
import string
import json

from .main import app
from .config import METABOTNIK_DATABASE

DATABASE_URL = f"sqlite:///{METABOTNIK_DATABASE}"
metabotnik_database = databases.Database(DATABASE_URL)


def escape(param):
    # As we need to use string formatting to access a table name, this leaves us open to SQL injection attacks :-(
    # The route to go would be looking into sqlite sql syntax for referencing table names dynamically in the queries
    return "".join(
        [ch for ch in param.lower() if ch in string.ascii_lowercase + string.digits]
    )


@app.get(
    "/metabotnik/xy/{projectname}/{x:float}_{y:float}",
    response_class=PlainTextResponse,
    include_in_schema=False,
)
async def xy(projectname: str, x: float, y: float):
    projectname = escape(projectname)
    query = (
        "SELECT obj FROM %s_objs WHERE id IN (SELECT id FROM %s_index WHERE x1 <= :x1 AND x2 >= :x2 AND y1 <= :y1 AND y2 >= :y2)"
        % (projectname, projectname)
    )
    results = await metabotnik_database.fetch_all(
        query, values={"x1": x, "x2": x, "y1": y, "y2": y}
    )
    if not results:
        raise HTTPException(status_code=404)

    anid = results[0][0]
    response = PlainTextResponse(anid)

    return response


@app.get(
    "/metabotnik/xy_wh/{projectname}/{x:float}_{y:float}",
    response_class=JSONResponse,
    include_in_schema=False,
)
async def xy_wh(projectname: str, x: float, y: float):
    projectname = escape(projectname)
    query = f"SELECT O.obj, I.x1, I.x2, I.y1, I.y2 FROM {projectname}_objs AS O LEFT JOIN {projectname}_index AS I ON O.id = I.id WHERE I.x1 <= :x1 AND I.x2 >= :x2 AND I.y1 <= :y1 AND I.y2 >= :y2"
    results = await metabotnik_database.fetch_all(
        query, values={"x1": x, "x2": x, "y1": y, "y2": y}
    )
    if not results:
        raise HTTPException(status_code=404)

    obj, x1, x2, y1, y2 = results[0]

    response = JSONResponse(
        {"obj": json.loads(obj), "x1": x1, "x2": x2, "y1": y1, "y2": y2},
    )

    return response


@app.get(
    "/metabotnik/tag_wh/{projectname}/{tag}",
    response_class=JSONResponse,
    include_in_schema=False,
)
async def tag_wh(projectname: str, tag: str):
    projectname = escape(projectname)
    tag = tag + "%"
    query = f"SELECT I.x1, I.x2, I.y1, I.y2 FROM {projectname}_tags AS T LEFT JOIN {projectname}_index AS I ON I.id = T.obj_id WHERE T.tag LIKE :tag"
    results = await metabotnik_database.fetch_all(query, values={"tag": tag})
    if not results:
        raise HTTPException(status_code=404)

    x1, x2, y1, y2 = results[0]

    response = JSONResponse({"x1": x1, "x2": x2, "y1": y1, "y2": y2})

    return response


@app.get(
    "/metabotnik/{projectname}", response_class=JSONResponse, include_in_schema=False
)
async def project(projectname: str):
    projectname = escape(projectname)
    results = await metabotnik_database.fetch_all(
        "SELECT name, width, height FROM projects WHERE name = :projectname",
        values={"projectname": projectname},
    )
    if not results:
        raise HTTPException(status_code=404)

    name, width, height = results[0]

    response = JSONResponse({"name": name, "width": width, "height": height})

    # Consider adding the number of objects from a count(*) query too.

    return response

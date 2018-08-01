from typing import List
import datetime

from data.proyecto import Proyecto


def find_all_proyectos() -> List[Proyecto]:
    proyectos = [
        proyecto.to_dict() for proyecto in Proyecto.objects().all()
    ]
    return proyectos


def get_proyecto_by_id(proyecto_id: str) -> Proyecto:
    proyecto = Proyecto.objects().get(id=proyecto_id)
    return proyecto


def find_all_by_padre_id(padre_id: str) -> List[Proyecto]:
    proyectos = [
        proyecto.to_dict() for proyecto in Proyecto.objects(padreId=padre_id)
    ]
    return proyectos

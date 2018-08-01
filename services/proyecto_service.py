from typing import List
import datetime

from data.proyecto import Proyecto


def persist_proyecto(proyecto_id: str,
                     nombre: str,
                     descripcion: str,
                     correo_creador: str,
                     id_seccion: str,
                     svg_id: str,
                     organizacion_id: str,
                     padre_id: str) -> Proyecto:
    proyecto = Proyecto()
    proyecto.id = proyecto_id
    proyecto.fecha_creacion = datetime.datetime.now()
    proyecto.nombre = nombre
    proyecto.descripcion = descripcion
    proyecto.correo_creador = correo_creador
    proyecto.id_seccion = id_seccion
    proyecto.svg_id = svg_id
    proyecto.organizacion_id = organizacion_id
    proyecto.padre_id = padre_id

    proyecto.save()

    return proyecto


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
        proyecto.to_dict() for proyecto in Proyecto.objects(padre_id=padre_id)
    ]
    return proyectos

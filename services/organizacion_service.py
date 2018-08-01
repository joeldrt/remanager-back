from typing import List

from data.organizacion import Organizacion

def find_all_organizaciones() -> List[Organizacion]:
    organizacion = [
        organizacion.to_dict() for organizacion in Organizacion.objects().all()
    ]
    return organizacion


def get_organizacion_by_id(organizacion_id: str) -> Organizacion:
    organizacion = Organizacion.objects().get(id=organizacion_id)
    return organizacion
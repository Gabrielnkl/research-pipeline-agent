def build_step(name, status, detail=None):
    return {
        "id": name.lower().replace(" ", "_"),
        "name": name,
        "status": status,
        "detail": detail,
    }


def update_steps(existing, name, status, detail=None):
    steps = existing or []

    found = False
    for s in steps:
        if s["name"] == name:
            s["status"] = status
            if detail:
                s["detail"] = detail
            found = True

    if not found:
        steps.append({
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "status": status,
            "detail": detail,
        })

    return steps
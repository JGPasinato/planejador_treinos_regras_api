from fastapi.responses import JSONResponse

MENSAGENS = {
    "missing": "campo obrigatório",
    "literal_error": "valor inválido, use: {expected}",
    "greater_than_equal": "deve ser maior ou igual a {ge}",
    "float_parsing": "deve ser um número",
    "int_parsing": "deve ser um número inteiro",
    "datetime_parsing": "data e hora inválidas, use o formato 2026-09-25T06:00:00",
    "datetime_from_date_parsing": "data e hora inválidas, use o formato 2026-09-25T06:00:00",
    "json_invalid": "JSON inválido",
}


def erro_validacao(request, exc):
    erros = []
    for erro in exc.errors():
        campo = ".".join(str(p) for p in erro["loc"] if p not in ("body", "query", "path"))
        ctx = erro.get("ctx", {})
        if "expected" in ctx:
            ctx["expected"] = ctx["expected"].replace("'", "").replace(" or ", ", ")
        try:
            mensagem = MENSAGENS[erro["type"]].format(**ctx)
        except KeyError:
            mensagem = "valor inválido"
        erros.append(f"{campo}: {mensagem}" if campo else mensagem)
    return JSONResponse(status_code=422, content={"detail": "; ".join(erros)})

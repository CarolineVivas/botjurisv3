from app.service.sanitize import sanitize_dict

dados = {
    "user": "<script>alert('xss')</script>",
    "mensagem": "   Olá   mundo!   ",
    "comando": "echo $HOME && ls"
}

print(sanitize_dict(dados))

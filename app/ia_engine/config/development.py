"""
    IA Engine Development Settings.
    Aqui estão todas as configurações utilizadas de itens que são utilizados apenas
    em ambiente de desenvolvimento.
    Aqui deverá conter apenas configurações extras e tools que são exclusivas para ambiente
    de desenvolvimento.
"""

NOTEBOOK_TOKEN = "9af4281a72a20cad133932da58a59ba8407e25d649a8cabd"

NOTEBOOK_ARGUMENTS = [
    "--ip",
    "0.0.0.0",
    "--port",
    "8888",
    "--allow-root",
    "--no-browser",
    "--NotebookApp.token={}".format(NOTEBOOK_TOKEN),
]
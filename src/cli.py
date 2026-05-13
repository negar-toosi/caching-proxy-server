import typer

from src.client.services import caching_proxy

app = typer.Typer()
app.command()(caching_proxy)

if __name__ == "__main__":
    app()

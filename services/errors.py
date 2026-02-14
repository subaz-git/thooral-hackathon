import click
from googleapiclient.errors import HttpError


def echo_error(action, message, hint=None):
    click.echo(f"Error [{action}]: {message}")
    if hint:
        click.echo(f"Hint: {hint}")


def echo_warning(action, message):
    click.echo(f"Warning [{action}]: {message}")


def echo_api_error(action, error):
    status = getattr(getattr(error, "resp", None), "status", None)
    if status is not None:
        click.echo(f"Error [{action}]: Google API request failed (HTTP {status}).")
    else:
        click.echo(f"Error [{action}]: Google API request failed.")
    click.echo(f"Details: {error}")

    if status == 401:
        click.echo("Hint: Run 'python3 gsuite_cli.py auth login' and try again.")
    elif status == 400:
        click.echo("Hint: Validate IDs, ranges, and request payload values.")
    elif status == 403:
        click.echo("Hint: Ensure required API(s) are enabled and scopes are allowed.")
    elif status == 404:
        click.echo("Hint: Verify the resource ID and your access permissions.")
    elif status == 429:
        click.echo("Hint: Rate limited. Retry with backoff.")
    elif status is not None and status >= 500:
        click.echo("Hint: Google service error. Retry shortly.")


def echo_exception(action, error):
    if isinstance(error, HttpError):
        echo_api_error(action, error)
    else:
        echo_error(action, str(error))

import click

from services import docs_service
from services.auth_service import login as login_user
from services.auth_service import logout as logout_user
from services.config import CLIENT_SECRETS_FILE
from services.credentials import get_credentials
from services.errors import echo_error, echo_exception, echo_warning

@click.group()
def gsuite():
    """A CLI for interacting with Google Workspace (Docs, Sheets, Forms)."""
    pass

@gsuite.group()
def auth():
    """Authentication commands for Google Workspace."""
    pass

@auth.command()
def login():
    """Logs in to Google Workspace."""
    try:
        login_user()
        click.echo("Authentication successful. Credentials saved.")
    except FileNotFoundError as error:
        echo_error(
            "auth login",
            str(error),
            f"Download OAuth client credentials and place them at {CLIENT_SECRETS_FILE}.",
        )
    except Exception as error:
        echo_exception("auth login", error)

@auth.command()
def logout():
    """Logs out from Google Workspace."""
    try:
        result = logout_user()
    except Exception as error:
        echo_exception("auth logout", error)
        return

    if not result["credentials_found"]:
        click.echo("No local credentials found.")
        return

    if result["revocation_attempted"]:
        if result["token_revoked"]:
            click.echo("Refresh token revoked.")
        else:
            echo_warning(
                "auth logout",
                result["revoke_error"] or "Could not revoke refresh token.",
            )
    else:
        click.echo("No refresh token found to revoke.")

    if result["credentials_deleted"]:
        click.echo("Local credentials deleted.")

@gsuite.group()
def docs():
    """Commands for Google Docs."""
    pass

@docs.command()
@click.argument('title')
def create(title):
    """Creates a new Google Doc."""
    creds = get_credentials()
    if not creds:
        return

    try:
        document = docs_service.create_document(creds, title)
        click.echo(f"Created document with title: {title}")
        click.echo(f"Document ID: {document.get('documentId')}")
        click.echo(f"Document URL: https://docs.google.com/document/d/{document.get('documentId')}/edit")
    except Exception as error:
        echo_exception("docs create", error)


@docs.command()
def list():
    """Lists Google Docs."""
    creds = get_credentials()
    if not creds:
        return

    try:
        items = docs_service.list_documents(creds)

        if not items:
            click.echo('No documents found.')
        else:
            click.echo('Documents:')
            for item in items:
                click.echo(f"{item['name']} ({item['id']})")
    except Exception as error:
        echo_exception("docs list", error)


@docs.command()
@click.argument('document_id')
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['plain_text', 'markdown'], case_sensitive=False),
    default='plain_text',
    show_default=True,
    help='Output format for document content.',
)
@click.option('--output', 'output_path', help='Save content to a local file path.')
def get(document_id, output_format, output_path):
    """Gets the content of a Google Doc."""
    creds = get_credentials()
    if not creds:
        return

    try:
        summary = docs_service.get_document_summary(creds, document_id)
        selected_format = output_format.lower()
        rendered_content = docs_service.render_content(
            summary["title"],
            summary["content"],
            selected_format,
        )

        if output_path:
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(rendered_content)
            click.echo(
                f"Document content saved to '{output_path}' in {selected_format} format."
            )
            return

        if selected_format == "markdown":
            click.echo(rendered_content, nl=False)
            return

        click.echo(f"Document Title: {summary['title']}")
        click.echo(f"Document ID: {summary['document_id']}")
        click.echo("\nContent:")
        if rendered_content:
            click.echo(rendered_content, nl=False)
        else:
            click.echo("Document is empty or has no readable content.")
    except Exception as error:
        echo_exception("docs get", error)

@docs.command()
@click.argument('document_id')
@click.option('--yes', is_flag=True, help='Skip delete confirmation prompt.')
def delete(document_id, yes):
    """Deletes a Google Doc."""
    creds = get_credentials()
    if not creds:
        return

    if not yes:
        confirmed = click.confirm(
            f"Delete document '{document_id}'?",
            default=False,
        )
        if not confirmed:
            click.echo("Delete cancelled.")
            return

    try:
        docs_service.delete_document(creds, document_id)
        click.echo(f"Document with ID '{document_id}' deleted successfully.")
    except Exception as error:
        echo_exception("docs delete", error)


@docs.command()
@click.argument('document_id')
@click.argument('new_title')
def copy(document_id, new_title):
    """Copies a Google Doc with a new title."""
    creds = get_credentials()
    if not creds:
        return

    try:
        copied_doc = docs_service.copy_document(creds, document_id, new_title)
        copied_id = copied_doc.get("id")
        click.echo(f"Copied document to: {copied_doc.get('name')} ({copied_id})")
        click.echo(f"Document URL: https://docs.google.com/document/d/{copied_id}/edit")
    except Exception as error:
        echo_exception("docs copy", error)


@docs.command(name='share')
@click.argument('document_id')
@click.option('--email', required=True, help='Email address to share with.')
@click.option(
    '--role',
    required=True,
    type=click.Choice(['reader', 'writer', 'commenter'], case_sensitive=False),
    help='Permission role to grant.',
)
def share_document(document_id, email, role):
    """Shares a Google Doc with an email and role."""
    creds = get_credentials()
    if not creds:
        return

    try:
        selected_role = role.lower()
        docs_service.share_document(creds, document_id, email, selected_role)
        click.echo(
            f"Shared document '{document_id}' with '{email}' as '{selected_role}'."
        )
    except Exception as error:
        echo_exception("docs share", error)

@docs.command()
@click.argument('document_id')
@click.option('--append', help='Text content to append to the document.')
@click.option('--set', 'set_content', help='Replace all document content with this text.')
def edit(document_id, append, set_content):
    """Edits a Google Doc using --append or --set."""
    creds = get_credentials()
    if not creds:
        return

    if append is None and set_content is None:
        echo_error("docs edit", "Provide one edit mode: --append or --set.")
        return

    if append is not None and set_content is not None:
        echo_error("docs edit", "Use only one mode at a time: --append or --set.")
        return

    try:
        if append is not None:
            if not append:
                echo_error("docs edit", "--append requires non-empty text.")
                return
            docs_service.append_text(creds, document_id, append)
            click.echo(f"Text appended to document ID '{document_id}' successfully.")
            return

        docs_service.set_text(creds, document_id, set_content or "")
        click.echo(f"Document ID '{document_id}' content replaced successfully.")
    except Exception as error:
        echo_exception("docs edit", error)

if __name__ == '__main__':
    gsuite()

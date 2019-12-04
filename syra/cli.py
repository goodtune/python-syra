from operator import itemgetter

import click
import ujson as json
from syra import API

##############################################################################
# Root Level Group and related operations                                    #
##############################################################################


@click.group()
@click.pass_context
@click.option("--reseller-id", envvar="RESELLER_ID")
@click.option("--api-key", envvar="API_KEY")
@click.option("--verify/--insecure", envvar="PYTHONSSLVERIFY", default=True)
def cli(ctx, reseller_id, api_key, verify):
    ctx.obj["api"] = API(reseller_id, api_key, verify=verify)


@cli.command()
@click.pass_context
def auth(ctx):
    """
    validate your credentials
    """
    res = ctx.obj["api"].authenticate()
    click.secho(
        u"\u2713 " if res else u"\u2717 ", nl=False, fg="green" if res else "red"
    )
    if not res:
        raise click.ClickException("Authentication failed.")
    click.echo("Authentication successful.")


@cli.command()
@click.pass_context
def balance(ctx):
    """
    report your account balance
    """
    click.echo(ctx.obj["api"].balance())


##############################################################################
# Contacts                                                                   #
##############################################################################


@cli.group()
@click.pass_context
def contact(ctx):
    """
    customer account operations
    """


@contact.command("list")
@click.pass_context
def contact_list(ctx):
    for item in ctx.obj["api"].contact_list():
        click.echo(item)


##############################################################################
# Domains                                                                    #
##############################################################################


@cli.group()
@click.pass_context
def domain(ctx):
    """
    domain name operations
    """


@domain.command("check", help="if domains are able to be registered")
@click.argument("domain", nargs=-1)
@click.pass_context
def domain_check(ctx, domain):
    if not domain:
        return
    for name, res in ctx.obj["api"].domain_check(*domain):
        click.secho(
            u"\u2713 " if res else u"\u2717 ", nl=False, fg="green" if res else "red"
        )
        click.secho(name)


@domain.command("info")
@click.argument("domain")
@click.option("-i", "--indent", count=True)
@click.pass_context
def domain_info(ctx, domain, indent):
    info = ctx.obj["api"].domain_info(domain)
    click.echo(json.dumps(info, indent=indent, sort_keys=True))


@domain.command("list", help="the domains in your account")
@click.option("-d", "--date-sort", is_flag=True, default=False)
@click.option("-r", "--reverse", is_flag=True, default=False)
@click.option("-x", "--expiring", is_flag=True, default=False)
@click.pass_context
def domain_list(ctx, date_sort, reverse, expiring):
    for name, status, expires in sorted(
        ctx.obj["api"].domain_list(),
        key=itemgetter(2 if date_sort else 0),
        reverse=reverse,
    ):
        ok = status == "Registered"
        if expiring and ok:
            continue
        click.secho(
            u"\u2713 " if ok else u"\u2717 ", nl=False, fg="green" if ok else "red"
        )
        click.secho(expires.strftime("%d-%b-%Y "), nl=False, fg="yellow")
        click.secho(name)


@domain.command("price")
@click.pass_context
def domain_price_list(ctx):
    price_list = sorted(
        ctx.obj["api"].domain_price_list().items(), key=lambda s: s[1]["Price"]
    )
    for tld, data in price_list:
        click.echo("{} {MinimumPeriod} {Price}".format(tld, **data))


@domain.command("renew", help="an existing domain")
@click.argument("domain")
@click.argument("period")
@click.pass_context
def domain_renew(ctx, domain, period):
    res = ctx.obj["api"].domain_renew(domain, period)
    ok = res["Status"] == "Registered"
    click.secho(u"\u2713 " if ok else u"\u2717 ", nl=False, fg="green" if ok else "red")
    click.secho(res["Expiry"].strftime("%d-%b-%Y "), nl=False, fg="yellow" if ok else "magenta", bold=True)
    click.secho(domain)


def main():
    cli(obj={}, auto_envvar_prefix="SYRA")


if __name__ == "__main__":
    main()

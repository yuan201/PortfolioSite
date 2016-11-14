from PortfolioSite.celery import app


@app.task
def task_get_quote(security, quoter, start, end):
    return quoter.get_quotes(security, start, end)


import os, click

def register(app):
    @app.cli.group()
    def upload():
        """Bulk upload and CLI Processing"""
        pass

    @upload.command()
    def test():
        """foo"""
        if app.config['SQLALCHEMY_DATABASE_URI']:
            print(app.config['SQLALCHEMY_DATABASE_URI'])
        else:
            raise RuntimeError('upload command failed')

    @upload.command()
    @click.argument('sid', type=click.INT)
    @click.argument('dir')
    def results(sid, dir):
        """Pull all res files into the app DB"""
        dbf = app.config['SQLALCHEMY_DATABASE_URI']
        #dir = os.path.join(os.getcwd(), dir)
        if not os.path.isdir(dir): raise RuntimeError('upload command failed')
        os.system('cli/load_results.py {} {} {}'.format(dbf, sid, dir))

    @upload.command()
    @click.argument('sid', type=click.INT)
    @click.argument('dir')
    def enrich(sid, dir):
        """Pull all res files into the app DB"""
        dbf = app.config['SQLALCHEMY_DATABASE_URI']
        #dir = os.path.join(os.getcwd(), dir)
        if not os.path.isdir(dir): raise RuntimeError('upload command failed')
        os.system('cli/load_enrich.py {} {} {}'.format(dbf, sid, dir))

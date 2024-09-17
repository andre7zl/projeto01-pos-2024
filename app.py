from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

# Configuração do OAuth com SUAP
oauth.register(
    name='suap',
    client_id="7i0DA1boDdPjsJzU8XsZotd9pN2WvNa4S2k0vGpe",
    client_secret="Yam8stQwobWopXwgt9duaCzCEOFPub3dk7KjFL5dDI7i3Bd2i6O8EUXJ1ADiJCDUU3rgBthJverwWmeoCccJWY3MuVArHMhos6VuH1ftPbcgIR62Qfp20eZVOqMzE37u",
    api_base_url='https://suap.ifrn.edu.br/api/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/',
    fetch_token=lambda: session.get('suap_token'),
    save_token=lambda token: session.update(suap_token=token)  # Atualiza token se necessário
)

# Rota principal
@app.route('/')
def index():
    if 'suap_token' in session:
        try:
            # Tentativa de acessar os dados do usuário
            meus_dados = oauth.suap.get('v2/minhas-informacoes/meus-dados')
            return render_template('user.html', user_data=meus_dados.json())
        except OAuthError as error:
            # Tratamento do erro de autenticação
            print(f"Erro de OAuth: {error.error} - {error.description}")
            return redirect(url_for('login'))
    else:
        return render_template('index.html')

# Rota de login
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))

# Rota para processar a autorização e salvar o token
@app.route('/login/authorized')
def auth():
    try:
        token = oauth.suap.authorize_access_token()
        session['suap_token'] = token
        return redirect(url_for('index'))
    except OAuthError as error:
        print(f"Erro durante a autorização: {error.error} - {error.description}")
        return redirect(url_for('index'))

# Rota para exibir o boletim
@app.route('/boletim')
def boletim():
    ano = request.args.get('ano', '2021')  # Pega o ano da consulta, padrão é 2021
    if 'suap_token' in session:
        try:
            # Obter dados do boletim para o ano selecionado
            boletim_data = oauth.suap.get(f'v2/minhas-informacoes/boletim/{ano}/1/')
            return render_template('notas.html', boletim_data=boletim_data.json(), ano=ano)
        except OAuthError as error:
            print(f"Erro ao acessar o boletim: {error.error} - {error.description}")
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()

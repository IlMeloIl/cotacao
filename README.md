# Dashboard de Cotações de Moedas

## Descrição

Aplicação web desenvolvida em Django que apresenta um dashboard para visualização de cotações de moedas (Real Brasileiro - BRL, Euro - EUR, Iene Japonês - JPY) em relação ao Dólar Americano (USD). Os dados são obtidos da API [Vatcomply](https://vatcomply.com/) e exibidos em gráficos.

**Acesse a aplicação em produção:** [https://jgvrm-5028f947afbc.herokuapp.com/](https://jgvrm-5028f947afbc.herokuapp.com/)

**_Nota: A aplicação busca por novas cotações diariamente. Como os mercados de câmbio globais fecham nos fins de semana e em feriados internacionais, os dados para esses dias refletem as cotações de fechamento do último dia útil anterior._**

## Funcionalidades Principais

*   **Dashboard**: Visualize cotações de moedas através de gráficos de linha e barra.
*   **Filtros Personalizados**: Selecione o período (data de início e fim) e as moedas de interesse (BRL, EUR, JPY).
*   **Múltiplas Visualizações Gráficas**:
    *   **Valores Absolutos**: Cotação direta USD/Moeda.
    *   **Variação Percentual**: Mudança percentual em relação ao início do período selecionado.
    *   **Performance/Valorização**: Gráfico de barras mostrando a valorização de cada moeda em relação ao USD no período.
*   **API REST**: Endpoints para acesso programático aos dados de cotações.

## Tecnologias Utilizadas

*   **Backend**:
    *   Python 3.13+
    *   Django 5.2+
    *   Django REST framework
*   **Frontend**:
    *   HTML5
    *   CSS3
    *   JavaScript
    *   Highcharts (para os gráficos)
*   **Banco de Dados**:
    *   PostgreSQL (em produção no Heroku)
    *   SQLite (para desenvolvimento local, configurável)
*   **APIs Externas**:
    *   Vatcomply API

## Configuração e Execução Local

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local utilizando `uv`.

### 1. Pré-requisitos

*   [uv](https://github.com/astral-sh/uv) instalado
*   Git

### 2. Clonando o Repositório

```bash
git clone https://github.com/IlMeloIl/cotacao
cd cotacao
```

### 3. Configurando o Ambiente Virtual com uv
O uv pode criar e gerenciar ambientes virtuais. Execute no diretório raiz do projeto:
```bash
uv sync
```

Isso criará um ambiente virtual chamado .venv (por padrão) e o ativará automaticamente no seu shell atual, se suportado, ou fornecerá o comando para ativação manual. Se não ativar automaticamente, use:
```bash
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 4. Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto com as seguintes variáveis:
```bash
SECRET_KEY='chave_secreta_aqui_para_desenvolvimento'
DEBUG=True
# DATABASE_URL='sqlite:///db.sqlite3' # Para usar SQLite localmente (padrão se não definido)
# Para usar PostgreSQL localmente (exemplo):
# DATABASE_URL='postgres://usuario:senha@localhost:5432/nome_do_banco'
```

### 5. Migrações do Banco de Dados
Aplique as migrações para criar as tabelas no banco de dados:
```bash
python manage.py migrate
```

### 6. Populando o Banco de Dados com Cotações
O projeto inclui um comando para buscar cotações da API Vatcomply e salvá-las no banco de dados.

* Para buscar cotações para o dia atual:
```bash
python manage.py buscar_cotacoes
```
* Para buscar cotações para uma data específica (formato AAAA-MM-DD):
```bash
python manage.py buscar_cotacoes --data AAAA-MM-DD
```
* Para buscar cotações para um intervalo de datas (formato AAAA-MM-DD):
```bash
python manage.py buscar_cotacoes --inicio AAAA-MM-DD --fim AAAA-MM-DD
```

### 7. Executando o Servidor de Desenvolvimento
Inicie o servidor de desenvolvimento do Django:
```bash
python manage.py runserver
```

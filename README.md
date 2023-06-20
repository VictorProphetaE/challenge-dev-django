# Projeto com Docker, Celery e Django Rest Framework

Este repositório contém um aplicativo Django para gerenciar propostas com campos dinâmicos. 
O aplicativo permite criar propostas com campos personalizados e realizar avaliações.

## Requisitos

Certifique-se de ter os seguintes requisitos instalados em sua máquina:

- Docker
- Docker Compose

- Django==3.2.4
- Celery==5.1.0
- djangorestframework==3.12.4

## Instalação

Siga as etapas abaixo para configurar e executar o projeto em um ambiente Docker:

1. Clone o repositório para a sua máquina local:
    `git clone VictorProphetaE/challenge-dev-django
3. Navegue até o diretório raiz do projeto.
    `cd <NOME_DO_DIRETORIO>`
   Nome do diretorio para onde foi clonado
4. Execute o seguinte comando para construir as imagens do Docker e iniciar os contêineres:
    `docker-compose up -d --build`
5. Após o comando ser executado com sucesso, você poderá acessar o aplicativo em seu navegador usando o seguinte URL:
    `http://localhost:8000`


## Criação de Usuário

Antes de começar a usar o aplicativo, você precisa criar um superusuário e um usuário dentro do ambiente Docker.

Para criar um superusuário, execute o seguinte comando dentro do contêiner Docker:
    `docker exec -it <nome do contêiner> python manage.py createsuperuse`

Siga as instruções na linha de comando para fornecer um nome de usuário, endereço de e-mail e senha para o superusuário.

Para criar um usuário regular, você pode usar a interface de administração do Django. Acesse http://localhost:8000/admin/ em seu navegador da web e faça login usando as credenciais do superusuário. Em seguida, clique em "Usuários" e "Adicionar" para criar um novo usuário.

## Sobre o Aplicativo

O aplicativo de propostas permite criar propostas com campos dinâmicos. Os campos dinâmicos são definidos no modelo CampoDinamico e podem ser de diferentes tipos, como `CharField`, `IntegerField`, `FloatField`, etc.

Os usuários podem enviar propostas preenchendo os campos dinâmicos necessários. As propostas são salvas no modelo Proposta e estão associadas aos campos dinâmicos por meio do modelo `ValorCampoDinamico`.

Os usuários podem visualizar todas as propostas enviadas e seus respectivos valores de campo dinâmico. Essa funcionalidade é implementada na visualização `visualizar_propostas`.

O aplicativo possui as seguintes URLs:

- `/`: Página inicial com informações sobre as propostas.
- `/login`: Página de login para autenticação.
- `/logout`: Página para fazer logout do aplicativo.
- `/propostas/`: Página para visualizar todas as propostas cadastradas.
- `/propostas/enviar`: Página para enviar uma nova proposta.

## Documentação da API

O aplicativo também oferece uma API RESTful para gerenciar as propostas. Aqui estão algumas das principais URLs da API:

- `/api/propostas/`: Endpoint para listar e criar propostas.
- `/api/propostas/<id>/`: Endpoint para visualizar, atualizar e excluir uma proposta específica.

Consulte a documentação completa da API para obter mais detalhes sobre as URLs e os métodos disponíveis.

## Tarefas em segundo plano com Celery

O projeto utiliza o Celery para executar tarefas em segundo plano. O processamento de avaliação de propostas é executado em segundo plano quando uma nova proposta é enviada. O resultado da avaliação é atualizado automaticamente no aplicativo.


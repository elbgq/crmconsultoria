# CRM Consultoria

Sistema web de CRM (Customer Relationship Management) para uma empresa de consultoria. Cobre o ciclo comercial e operacional completo: cadastro de empresas e contatos, funil de vendas (lista e Kanban), registro de interações, conversão automática de oportunidade ganha em projeto, entregas/fases, tarefas e um painel de relatórios gerenciais.

- **Desenvolvedor:** Eloi
- **Situação:** em desenvolvimento (versão funcional; MVP interno)
- **Período de desenvolvimento registrado:** 21/07/2026 a 27/08/2026 (git: 08 commits, de 19/08 a 27/08/2026)
- **Repositório:** `D:\DATA\Aplicativos\crm_consultoria` (aplicação Django em `crm_consultoria/`, projeto independente)
- **Produção:** PythonAnywhere (`eloibgq.pythonanywhere.com`)

---

## 1. Stack

| Camada | Tecnologia |
|---|---|
| Linguagem / framework | Python + Django 5.2 (apps com *class-based views* e *function views*) |
| Banco de dados | SQLite (`db.sqlite3`) |
| Front-end | Templates Django + Bootstrap 5.3.3 (CDN), jQuery 3.6 e Bootstrap Datepicker (pt-BR) |
| Kanban | SortableJS 1.15.2 + `fetch` (AJAX) |
| Gráficos | Chart.js 4.4.0 |
| Configuração | `python-dotenv` (`SECRET_KEY`, `DEBUG` no `.env`) |
| Imagens | Pillow (foto do perfil) |
| Idioma / fuso | `pt-br` / `America/Sao_Paulo` |

## 2. Estrutura do projeto

```
crm_consultoria/        configurações (settings, urls, wsgi/asgi)
crm_core/               modelo base de auditoria, enums do negócio, Home (painel inicial)
clientes/               EmpresaCliente, Contato + comandos de importação
oportunidades/          Oportunidade, HistoricoEstagio, lista, Kanban, signals
interacoes/             Interacao (ligação, e-mail, reunião, WhatsApp, visita)
projetos/               ProjetoConsultoria, Entrega, progresso e status automáticos
tarefas/                Tarefa (prioridade, tipo, vínculo, vencimento)
relatorios/             dashboard e camada de serviços (services.py)
usuarios/               Perfil (cargo, área), permissões por cargo, signal de criação
templates/              base.html, login e troca de senha
static/css/             4 temas: pastel (ativo), dark mode, minimal, old
fixtures/               oportunidade_exemplo_fixture.json (dados de exemplo)
```

## 3. Como executar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# criar .env com SECRET_KEY=... e DEBUG=True (nunca commitar o .env)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Dados de exemplo: `python manage.py loaddata fixtures/oportunidade_exemplo_fixture.json`

---

## 4. Fases do projeto

> **Sobre os tempos.** As datas (calendário) vêm do histórico do git e da data de criação/modificação dos arquivos. As **horas são estimativas** de esforço líquido, calculadas a partir do volume de código e da complexidade de cada fase — não são horas apontadas. O total gira em torno de **100 a 125 horas**, distribuídas em ~5 semanas de calendário. Ajuste os valores se houver apontamento real.

| # | Fase | Período | Esforço estimado | Situação |
|---|---|---|---|---|
| 1 | Fundação e modelagem | 21/07 – 22/07 | 8–10 h | Concluída |
| 2 | Clientes e contatos | 22/07 – 23/07 | 10–12 h | Concluída |
| 3 | Usuários, perfis e permissões | 23/07 | 6–8 h | Concluída (permissões ainda pouco aplicadas) |
| 4 | Oportunidades e funil de vendas | 23/07 – 19/08 | 16–20 h | Concluída |
| 5 | Kanban de oportunidades | 19/08 – 23/08 | 8–10 h | Concluída |
| 6 | Interações com clientes | 23/07 – 24/08 | 6–8 h | Concluída |
| 7 | Projetos e entregas | 23/07 – 24/08 | 12–15 h | Concluída |
| 8 | Tarefas | 23/07 – 24/08 | 8–10 h | Concluída |
| 9 | Relatórios e dashboard | 23/07 – 23/08 | 8–10 h | Concluída (base) |
| 10 | Importação de dados legados | até 19/08 | 6–8 h | Concluída |
| 11 | Interface, temas e usabilidade | 25/07 – 27/08 | 10–12 h | Concluída |
| 12 | Implantação (PythonAnywhere) | até 19/08 | 4–6 h | Concluída (sem automação) |
| 15 | Lançamento de horas | 09/10 | 10–14 h | Concluída |
| 13 | Testes, qualidade e endurecimento | 08/10 | 6–8 h | Concluída (58 testes; correções aplicadas) |

### Fase 1 — Fundação e modelagem (≈ 8–10 h · 21/07 – 22/07)
- Criação do projeto Django, ambiente virtual e organização em apps por domínio.
- `settings.py`: `.env` com `python-dotenv`, `SECRET_KEY` obrigatória, `DEBUG` por variável, localização pt-BR, fuso de São Paulo, URLs de login/logout.
- `crm_core`: `ModeloBase` (abstrato, `criado_em`/`atualizado_em`) e enums do negócio: `EstagioFunil` (Prospecção → Qualificação → Proposta → Negociação → Ganho/Perdido), `TipoContrato` (projeto fechado, banco de horas, retainer, fee de êxito) e `AreaConsultoria` (estratégia, financeira, processos, RH, comercial, TI).
- Template base com navbar e mensagens do sistema.

### Fase 2 — Clientes e contatos (≈ 10–12 h · 22/07 – 23/07)
- `EmpresaCliente`: razão social, fantasia, CNPJ, setor, porte (MEI/pequena/média/grande), website, modalidade (comprador/vendedor), observações.
- `Contato` ligado à empresa (cargo, e-mail, telefone, flag de decisor).
- CRUD completo da empresa (views genéricas) e do contato; lista paginada (20 por página) com busca por razão social/fantasia.
- Endpoint AJAX `contatos-por-empresa` para carregar contatos dinamicamente nos formulários.
- Páginas de detalhe da empresa e do contato, com confirmação de exclusão.

### Fase 3 — Usuários, perfis e permissões (≈ 6–8 h · 23/07)
- `Perfil` 1:1 com o usuário: cargo (Sócio, Consultor Sênior, Consultor, Administrativo), área principal, telefone, foto, ativo.
- *Signal* que cria o `Perfil` automaticamente a cada novo usuário.
- Funções de permissão por cargo (`eh_socio`, `eh_consultor_senior_ou_socio`).
- Login, logout e troca de senha com telas personalizadas; acesso restrito a usuários autenticados.
- Admin do Django para gestão administrativa.

### Fase 4 — Oportunidades e funil de vendas (≈ 16–20 h · 23/07 – 19/08)
- `Oportunidade`: empresa, contato principal, consultor responsável, área, tipo de contrato, valor estimado, horas estimadas e valor/hora, probabilidade, estágio, origem, datas (início previsto, duração, fechamento real), motivo de perda e observações. Índices por estágio, consultor e fechamento.
- `HistoricoEstagio`: trilha de auditoria de cada mudança de estágio (anterior, novo, data, autor).
- *Signals* para registrar o histórico automaticamente na criação e em cada mudança de estágio.
- CRUD completo, lista com filtros e página de detalhe (histórico, interações e tarefas vinculadas).
- Ação “mudar estágio” e registro do motivo de perda (concorrência, preço, prazo, escopo inadequado, desinteresse).

### Fase 5 — Kanban de oportunidades (≈ 8–10 h · 19/08 – 23/08)
- Quadro com uma coluna por estágio do funil, cartões das oportunidades e arrastar-e-soltar com SortableJS.
- Atualização do estágio via AJAX (`atualizar-estagio`), com validação do estágio e criação do histórico.
- Ao mover para **Perdido**, o sistema pede o motivo da perda.
- Orientações ao usuário na própria tela (commit de 19/08).

### Fase 6 — Interações com clientes (≈ 6–8 h · 23/07 – 24/08)
- `Interacao`: tipo (ligação, e-mail, reunião, WhatsApp, visita, outro), assunto, descrição, data/hora, responsável.
- Vinculada obrigatoriamente ao contato (`CASCADE`) e opcionalmente à oportunidade (`SET_NULL`, preservando o histórico de relacionamento).
- Registro a partir do contato ou da oportunidade; edição e exclusão; índices para consulta cronológica.
- Reestruturação do funcionamento das interações em 24/08.

### Fase 7 — Projetos e entregas (≈ 12–15 h · 23/07 – 24/08)
- `ProjetoConsultoria` 1:1 com a oportunidade de origem: status, equipe (N:N), gerente, datas reais/previstas, horas estimadas e consumidas.
- **Criação automática do projeto** quando a oportunidade vira *Ganho* (signal + garantia no histórico, evitando duplicidade).
- `Entrega` (marcos/fases do projeto): data prevista/entregue, responsável, conclusão.
- Cálculos automáticos: percentual de horas consumidas, progresso por entregas concluídas, status automático (Não iniciado / Em andamento / Atrasado / Concluído), listas de fases atrasadas, pendentes e concluídas, cores de status.
- Alertas visuais de fases atrasadas no detalhe do projeto; tela de adicionar/editar/concluir entrega; lista, edição e exclusão de projetos.

### Fase 8 — Tarefas (≈ 8–10 h · 23/07 – 24/08)
- `Tarefa`: título, descrição, tipo, prioridade (baixa a urgente), responsável, vencimento, conclusão.
- Vínculo com oportunidade e projeto (vinculação de tarefas às respectivas oportunidades/projetos, 24/08), com validação em `clean()`.
- *Signal* que preenche/limpa `data_conclusao` ao marcar/desmarcar como concluída.
- Lista, criação com valores iniciais herdados do contexto, edição e ação “concluir”.

### Fase 9 — Relatórios e dashboard (≈ 8–10 h · 23/07 – 23/08)
- Camada `services.py` (consultas agregadas separadas das views, reutilizáveis por uma futura API).
- Indicadores: funil de vendas (quantidade e valor por estágio), conversão por consultor (total/ganhas/perdidas), receita por tipo de contrato e por área, margem de projetos (horas estimadas × consumidas, alerta acima de 90%) e tarefas atrasadas por responsável.
- Dashboard com gráficos Chart.js (funil e receita por área) e tabelas.
- Home com resumo: total de empresas, oportunidades abertas, valor em negociação, oportunidades por estágio e últimas oportunidades.

### Fase 10 — Importação de dados legados (≈ 6–8 h · até 19/08)
- Comandos de gerenciamento `importar_empresas_rodanegocios` e `importar_contatos_rodanegocios`, que leem o `db.sqlite3` de um sistema anterior e populam `EmpresaCliente` e `Contato`.
- Opção `--dry-run` para simular antes de gravar.
- Fixture de exemplo (`fixtures/oportunidade_exemplo_fixture.json`) para demonstração.

### Fase 11 — Interface, temas e usabilidade (≈ 10–12 h · 25/07 – 27/08)
- Bootstrap 5, datepicker em pt-BR e mensagens de feedback em todas as telas.
- Quatro folhas de estilo intercambiáveis: `style_pastel` (ativo), `style_darkmode`, `style_minimal` e `style_old` (alterações de 25/08 e 27/08).
- Ajustes de status de projetos e de fluxo visual (commit de 27/08).

### Fase 12 — Implantação (≈ 4–6 h · até 19/08)
- Hospedagem no PythonAnywhere com `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` configurados (alternativa comentada para túnel Ngrok em testes).
- Endurecimento ativado quando `DEBUG=False`: redirecionamento HTTPS, cookies de sessão/CSRF seguros, `X-Frame-Options: DENY`.
- `STATIC_ROOT` configurado para `collectstatic`.

### Fase 15 — Lançamento de horas (≈ 10–14 h · 09/10)
- Modelo `LancamentoHoras` (projeto, consultor, data, horas de 0,25 a 24, descrição); não aceita data futura.
- `horas_consumidas` do projeto deixou de ser digitado: é a **soma dos lançamentos**, recalculada por signal a cada criação, edição ou exclusão. O campo saiu do formulário do projeto e é somente leitura no Admin.
- Telas: lançar, editar e excluir horas, no detalhe do projeto, com total por consultor.
- Regra de acesso: qualquer usuário logado lança horas (sempre em seu nome); edita ou exclui só os próprios lançamentos — superusuário, sócio e consultor sênior gerenciam todos.
- Migração de dados (`projetos/0005`): horas já digitadas à mão viram lançamentos "Saldo anterior" (em blocos de até 24 h), preservando o total.
- A margem do dashboard passa a refletir horas reais. 69 testes no total.

### Fase 13 — Testes, qualidade e endurecimento (≈ 12–16 h · concluída)
Ver a seção 6 (correções aplicadas e pendências).

---

## 5. Regras de negócio implementadas

- Mudar o estágio de uma oportunidade gera registro em `HistoricoEstagio`.
- Oportunidade **ganha** gera automaticamente um **projeto** de consultoria (um por oportunidade).
- Excluir uma oportunidade **não** apaga as interações (ficam sem vínculo); excluir um contato apaga suas interações.
- O status do projeto é recalculado a cada gravação de uma entrega.
- Uma tarefa deve ficar ligada a uma oportunidade **ou** a um projeto, não aos dois.
- Margem de horas: alerta quando o projeto consome mais de 90% das horas estimadas.

## 6. Correções aplicadas e pendências

**Corrigido (08/10/2026)** — 23 testes automatizados, `check` e `makemigrations --check` verdes:
- **Histórico de estágio duplicado:** agora só o signal grava o `HistoricoEstagio`; as views apenas informam o autor (`_alterado_por`).
- **Criação de projeto:** ficou só em `projetos/signals.py` (removida a duplicata de `HistoricoEstagio.save()`), com nome "Projeto — título" e data de início.
- **Tarefa:** `oportunidade` passou a ser opcional (migration `tarefas/0003`); continua proibido vincular a oportunidade e projeto ao mesmo tempo.
- **Status "Atrasado":** incluído em `StatusProjeto` e usado por `atualizar_status()` (migration `projetos/0003`).
- `percentual_horas_consumidas` não quebra mais com `horas_consumidas` nulo.
- `probabilidade` limitada a 0–100 (migration `oportunidades/0003`).
- Removida a função morta `kanban_oportunidades`.
- **Permissões:** o dashboard de relatórios agora exige superusuário, sócio ou consultor sênior (403 para os demais), via `cargo_minimo_senior_required`.
- Comandos `importar_*_rodanegocios` sem caminho fixo: informe o caminho ou defina `RODANEGOCIOS_DB`.
- `requirements.txt` sem as dependências do Flask; criado `.env.example`; comentários do `settings.py` apontam para o Django 5.2.

**Segunda rodada (08/10/2026)** — 58 testes, rodando em ~2 s (hasher de senha simples só durante os testes):
- Regra de acesso mantida: apenas o dashboard é restrito (superusuário, sócio e consultor sênior). O link "Relatórios" some do menu para quem não tem acesso.
- Testes novos para clientes, contatos, interações, usuários/login, home e views de tarefas.
- Bugs de **tarefas** encontrados pelos testes e corrigidos: a lista quebrava (nomes de URL sem namespace), o "Cancelar" do formulário apontava para rota inexistente, criar tarefa falhava por falta de responsável (agora é o usuário logado) e editar/concluir não voltavam para a oportunidade/projeto.

**Ainda pendente**
- Aplicar restrições por cargo nas demais telas, quando a regra de quem vê o quê for definida.

## 7. Roadmap sugerido (próximas fases)

| Fase | Atividades | Esforço estimado |
|---|---|---|
| 13 — Testes e correções | Testes de modelos, signals, views e serviços; corrigir os defeitos acima; unificar o histórico de estágio e a criação de projeto | 20–30 h |
| 14 — Permissões por cargo | Aplicar `eh_socio`/`eh_consultor_senior_ou_socio` nas views; consultor vê só o que é seu | 8–10 h |
| 16 — Filtros e exportação | Filtros por período/consultor nos relatórios e exportação CSV/PDF | 8–12 h |
| 17 — Agenda e alertas | Lembretes de tarefas e entregas, e-mails de aviso | 10–14 h |
| 18 — Banco e deploy | Migrar para PostgreSQL, backup automático, `.env.example`, roteiro de deploy | 6–8 h |

## 8. Resumo do que existe hoje

- **8 apps Django**, 9 modelos de negócio (`EmpresaCliente`, `Contato`, `Oportunidade`, `HistoricoEstagio`, `Interacao`, `ProjetoConsultoria`, `Entrega`, `Tarefa`, `Perfil`) mais um modelo base abstrato, 14 migrations, 35 rotas nos apps e 28 templates.
- Funil comercial com Kanban, projetos gerados automaticamente, entregas com alertas de atraso, tarefas e painel gerencial.
- Em produção no PythonAnywhere; 69 testes cobrindo todos os apps.

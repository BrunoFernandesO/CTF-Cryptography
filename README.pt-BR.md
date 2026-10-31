# Criptografia na Prática

[English](README.md)

Materiais e plataforma de CTF de **"Criptografia na Prática: Matemática e Python do Zero ao RSA"**, um curso prático de dois dias e 8 horas, ministrado por Bruno Fernandes Ortega em 26 e 27 de outubro de 2026 no WorkInTech 2026 (6ª edição). O WorkInTech é o evento de tecnologia organizado pela Axion, a organização estudantil de tecnologia da UniCesumar, em Maringá.

O curso é em português, assim como os slides, os cadernos, os comentários do código e a interface do CTF.

## Público e resultados

- Cerca de 35 alunos, a maioria do primeiro e do segundo ano de Engenharia de Software e de Análise e Desenvolvimento de Sistemas.
- Todos os participantes resolveram os níveis 1 (César) e 2 (Vigenère) do CTF com código escrito por eles em aula.
- O algoritmo de Euclides, o RSA e o nível 3 do CTF foram preparados, mas não chegaram a ser dados. Os blocos práticos levaram cerca de 1,6 vez o tempo previsto, e a escolha foi aprofundar em vez de cobrir tudo.

## Abordagem

- **Os alunos escrevem os ataques, não só as cifras.** Depois de implementar o César, eles o quebram por força bruta e ensinam o Python a reconhecer português. Depois do Vigenère, acham o tamanho da chave com o índice de coincidência e quebram cada coluna como um César.
- **Esqueletos, não código pronto.** O código nos slides tem `???` onde o aluno escreve o passo que falta, marcado com `TODO`. As soluções estão nas notas do apresentador e em `reference/solucoes.py`.
- **Autoconferência.** Nos cadernos do Colab, cada exercício é seguido de uma célula "Conferir", que diz se a função está certa. Uma célula "Plano B" carrega as funções do dia 1 prontas, para ninguém ficar travado no dia 2.
- **Dois níveis de caderno.** O `caderno-aluno.ipynb` acompanha os slides. O `caderno-desafio.ipynb` tem TODOs maiores, para quem quer mais dificuldade.
- **O CTF acompanha as aulas.** O nível 1 vem depois do César, no dia 1; os níveis 2 e 3, depois do Vigenère e do RSA. Cada aluno roda o próprio código num puzzle que só ele recebeu.

## Como o CTF funciona

```text
 Alunos ("/")  --HTTP-->  Flask (app.py)  -->  SQLite (ctf.db)
                           |- puzzles.py: puzzles derivados de HMAC(segredo, apelido:nível:tentativa)
                           |- dá a cada aluno uma resposta que ninguém mais tem (UNIQUE no banco)
                           '- confere as flags só no servidor
 Telão ("/placar") <-- /api/placar a cada 3 s: ranking, primeiro a resolver cada nível, últimos acertos
 "/organizador"  --> painel com senha para abrir e fechar níveis durante a aula
 "/colab", "/desafio" --> endereços curtos para os dois cadernos, digitados nos computadores do laboratório
```

| Nível | Cifra | O que o aluno faz | Respostas diferentes |
| --- | --- | --- | --- |
| 1 · 100 pts | César, k de 1 a 25 | força bruta nas 25 chaves e lê a senha | 1.600 (40 termos × 40 animais) |
| 2 · 200 pts | Vigenère, chave de 3 a 7 letras | índice de coincidência para achar o tamanho da chave, depois um César por coluna | 131 chaves, todas testadas contra o ataque |
| 3 · 300 pts | RSA com p, q entre 200 e 1000 | fatorar n, calcular φ(n), d e m | praticamente ilimitadas |

Garantias:

- **Respostas únicas.** Na primeira vez que um aluno abre um nível, o servidor escolhe um puzzle cuja flag ninguém mais tem e grava a escolha. Copiar a flag de um colega não funciona. No nível 2, isso vale para até 131 jogadores.
- **Esperas.** Cada flag errada custa uma espera crescente, por jogador e por nível: 3 s nos 5 primeiros erros, 30 s nos 5 seguintes e depois 120 s. Testar a lista inteira de chaves não é viável.
- **Só durante a aula.** Cada nível tem um interruptor e começa fechado. Um nível fechado não envia o texto cifrado nem a dica, e o servidor recusa as flags dele. Ninguém resolve em casa com uma ferramenta online antes da aula.
- **Contas com apelido + PIN.** O aluno escolhe um PIN de 4 dígitos junto com o apelido e o usa para voltar à conta em outro computador no dia 2. Cinco PINs errados travam o apelido por 5 minutos. Se o aluno esquecer o PIN, o organizador libera o apelido, e os pontos e os puzzles são mantidos.

O modelo de dados, a derivação dos puzzles e o modelo de ameaças estão em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Rodar localmente

Python 3.8 ou mais novo.

```bash
cd ctf-server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app senha              # define a senha do organizador (8+ caracteres)
flask --app app abrir todos        # abre todos os níveis (eles começam fechados)
python app.py                      # http://localhost:5000, /placar, /organizador
```

A primeira execução cria `secret.key` e `ctf.db` em `ctf-server/`. Os dois são ignorados pelo git. Mantenha o `secret.key` entre os dois dias de uma turma: é ele que mantém os puzzles de cada aluno iguais.

Testes e soluções de referência, a partir da raiz do repositório:

```bash
pip install -r ctf-server/requirements.txt pytest
pytest                             # testes do CTF (tests/)
python reference/solucoes.py       # imprime "todos os testes passaram"
```

## Estrutura do repositório

```text
ctf-server/          servidor do CTF usado em aula (V4.3): app Flask, puzzles, templates, arquivos estáticos
notebooks/           cadernos do Colab: caderno-aluno e caderno-desafio
reference/           solucoes.py: o código dos slides com todos os TODOs preenchidos, com asserts
slides/
  criptografia-na-pratica-oficina.pptx   o deck de 37 slides usado em aula, em PowerPoint
  conteudo-37-slides.md                  texto e notas do apresentador desse deck
  prototype-html/                        primeiro protótipo em HTML, 34 slides (18/10)
tests/               testes do CTF com pytest; legacy/ guarda os scripts de validação originais
docs/                TIMELINE.md, ARCHITECTURE.md, CURRICULUM.md
```

## Linha do tempo

Tudo foi feito entre 14 e 26 de outubro de 2026. O repositório foi criado depois. Cada commit leva a data em que o seu conteúdo existia. Os horários estão em UTC−3. "aprox." marca um horário deduzido da ordem dos acontecimentos. Os detalhes estão em [docs/TIMELINE.md](docs/TIMELINE.md).

| Data | Versão | Fidelidade |
| --- | --- | --- |
| 14/10 22:08 | Gerador de puzzles do CTF e validação dos ataques | exata |
| 14/10 22:10 | CTF V1: servidor, página do aluno, placar do telão | exata |
| 14/10 22:12 | Verificador de estouro dos slides | exata |
| 18/10 10:28 | Protótipo do deck em HTML, 34 slides | exata |
| 18/10 10:33 | Soluções de referência | exata |
| 21/10 20:06 | CTF V2: respostas únicas, esperas crescentes, visual novo | exata |
| 21/10 21:50 | Caderno do aluno | exata (saídas removidas) |
| 21/10 23:23 | Caderno do aluno renumerado para o deck de 37 slides | exata (saídas removidas) |
| 21/10 23:51 | CTF V3: endereço curto /colab | exata |
| 25/10 11:00 aprox. | CTF V4: níveis abertos só na aula, painel do organizador | reconstruída |
| 25/10 16:53 | Caderno desafio | exata (saídas removidas) |
| 25/10 16:59 | CTF V4.2: endereço curto /desafio | exata |
| 25/10 17:33 | CTF V4.3: contas com apelido + PIN | exata |
| 25/10 19:30 aprox. | Texto e notas do deck de 37 slides | exata |
| 26/10 16:36 | Deck final em PowerPoint | exata, sem um rótulo de confidencialidade e sem dados de contato |

## Créditos

- A Axion e a organização do WorkInTech 2026, pelo evento e pela identidade visual usada nos slides e no CTF.
- Os alunos, que escreveram os ataques.

## Licença

- Código (`ctf-server/`, `reference/`, `tests/`): licença MIT, veja [LICENSE](LICENSE).
- Material didático (`slides/`, `notebooks/`, `docs/`, os arquivos README): Creative Commons Atribuição 4.0 Internacional, veja [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt).
- Fora das duas licenças: os logos da Axion e do WorkInTech e a imagem de fundo (`ctf-server/static/axion-logo.svg`, `wit-mark.png`, `fundo.jpg`, e as mesmas imagens nos slides) pertencem à Axion e são publicados com a permissão dela. Fotografias históricas e diagramas de terceiros nos slides seguem os próprios termos. As fontes embutidas no arquivo PowerPoint seguem as próprias licenças, listadas nas propriedades do arquivo.

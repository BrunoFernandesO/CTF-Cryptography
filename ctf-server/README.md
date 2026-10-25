# CTF de Criptografia · WorkInTech (Axion) · V4

Servidor do desafio final da oficina **Criptografia na Prática: Matemática e Python do Zero ao RSA**, ministrada por Bruno Fernandes Ortega no WorkInTech 2026 (Axion, UniCesumar). Cada aluno escolhe um apelido, recebe três puzzles próprios (César, Vigenère e RSA pequeno), quebra cada um com o código que escreveu na oficina e envia a flag. O placar do telão atualiza sozinho.

## Como funciona

```text
 Alunos ("/")  ──HTTP──►  Flask (app.py)  ──►  SQLite (ctf.db)
                           ├─ puzzles.py: gera os puzzles a partir de HMAC(segredo, apelido:nível:tentativa)
                           ├─ atribui a cada aluno uma resposta que ninguém mais tem (UNIQUE no banco)
                           └─ confere as flags só no servidor
 Telão ("/placar") ◄── /api/placar a cada 3 s: ranking, primeiro a resolver, últimos acertos
 "/colab" e "/caderno" ──► redirecionam para o caderno do aluno no Google Colab
 "/organizador" ──► painel com senha para abrir e fechar cada nível durante a aula
```

O endereço curto `/colab` existe porque os alunos programam nos computadores do laboratório: digitar `brunofernandeso.pythonanywhere.com/colab` é viável, a URL do Google Drive não. O destino fica na constante `COLAB_URL` do `app.py` (ou na variável de ambiente de mesmo nome).

| Nível | Cifra | O aluno precisa | Respostas diferentes |
| --- | --- | --- | --- |
| 1 · 100 pts | César, k de 1 a 25 | força bruta (25 chaves) e ler a senha | 1.600 senhas (40 termos × 40 animais) |
| 2 · 200 pts | Vigenère, chave de 3 a 7 letras | índice de coincidência para achar m, depois um César por coluna | 131 chaves, todas testadas contra o ataque |
| 3 · 300 pts | RSA com p, q entre 200 e 1000 | fatorar n, calcular φ(n), d e m | praticamente ilimitadas |

Garantias:

- **Níveis abrem só na aula (V4).** Cada nível tem um interruptor; o padrão é fechado. Fechado, a página não mostra o texto cifrado nem a dica e o servidor recusa flags, então ninguém resolve em casa com um site pronto. Os alunos veem o nível aparecer sozinho, em até 10 s, quando o organizador abre.
- **Nenhuma resposta repetida.** Na primeira vez que um aluno vê um nível, o servidor procura uma tentativa cuja flag ninguém mais tenha e grava essa escolha (`assignments`, com `UNIQUE (level, flag_key)`). No nível 2, isso vale até 131 jogadores; a partir daí as chaves voltam a se repetir.
- **Sem chute em massa.** Cada erro custa uma espera que cresce: 3 s nos primeiros 5 erros, 30 s do 6º ao 10º e 120 s depois disso (por jogador e por nível).
- **Flags tolerantes ao formato.** Maiúsculas ou minúsculas, espaço, hífen ou sublinhado: `flag{chave urso}` vale como `FLAG{CHAVE-URSO}`.

## Rodar localmente

```bash
cd ctf-server
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                                          # http://localhost:5000 e /placar
```

Na primeira execução é criado `secret.key` (o segredo dos puzzles). **Não apague** entre os dois dias da oficina. Ele e o `ctf.db` nunca vão para o Git (veja `.gitignore`).

## Publicar no PythonAnywhere

Aplicação web com configuração manual, Python 3.10 ou mais novo, virtualenv com `pip install -r requirements.txt` e o arquivo WSGI:

```python
import sys
path = "/home/<usuario>/ctf-server"
if path not in sys.path:
    sys.path.insert(0, path)
from app import app as application
```

Ao atualizar uma versão já publicada, substitua só os arquivos do código e **mantenha `secret.key` e `ctf.db`**. Depois, clique em **Reload** na aba Web.

## Comandos do organizador

```bash
flask --app app zerar               # apaga jogadores, pontos e puzzles (antes de cada turma)
flask --app app liberar APELIDO     # aluno perdeu o login: o próximo acesso com esse nome assume a conta
flask --app app respostas APELIDO   # mostra a resposta de um aluno, para ajudar quem travou
flask --app app senha               # cria ou troca a senha do painel /organizador (mínimo 8 caracteres)
flask --app app abrir 1             # abre níveis: abrir 2 3   |   abrir todos
flask --app app fechar todos        # fecha níveis
flask --app app status              # mostra o que está aberto
```

O painel `/organizador` faz o mesmo que `abrir` e `fechar`, pelo celular. Cinco senhas erradas bloqueiam o endereço por 5 minutos. O `zerar` não mexe na senha nem nos níveis abertos.

## Estrutura

```text
ctf-server/
├── app.py              rotas (inclusive /colab), banco, atribuição de respostas, comandos
├── puzzles.py          listas de palavras e chaves, geração dos puzzles, comparação de flags
├── templates/          index.html (alunos), placar.html (telão) e organizador.html (painel)
├── static/             ctf.css (tokens da identidade Axion), trilha.js, logos e fundo
└── requirements.txt    Flask
```

Identidade visual: sistema de design Axion (fundo roxo, acento lima, Lexend e JetBrains Mono). Logos da Axion e do WorkInTech pertencem à Axion.

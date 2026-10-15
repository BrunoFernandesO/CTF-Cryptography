# CTF de Criptografia · WorkInTech (Axion)

Servidor Flask + SQLite para rodar no **seu notebook**, na rede do laboratório. Cada aluno escolhe um apelido e recebe puzzles próprios (derivados de HMAC com um segredo do servidor), escreve o código do ataque e envia a flag. O placar atualiza sozinho e há uma página própria para o telão.

## 1. Instalar e rodar

```bash
cd ctf-server
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                                          # sobe na porta 5000
```

Na primeira execução é criado o arquivo `secret.key` (o segredo dos puzzles). **Não apague** entre os dois dias: ele garante que o puzzle de cada apelido continue o mesmo. Para trocar o evento, apague `secret.key` e rode `flask --app app zerar`.

## 2. Deixar os computadores do laboratório acessarem

1. Descubra o IP do notebook na rede: `ip a` (Linux), `ipconfig` (Windows) ou `ifconfig` (macOS). Algo como `192.168.x.x` ou `10.x.x.x`.
2. Libere a porta 5000 no firewall do notebook (Windows: permitir o Python na rede privada quando perguntado).
3. Nos alunos, o endereço será `http://SEU_IP:5000`. Gere o QR code desse endereço para o slide do CTF.
4. **Teste antes do dia 26**, no laboratório, com o celular e com um computador de lá. Algumas redes de laboratório e de universidade isolam os clientes entre si ("client isolation"), e aí nada disto funciona. Se acontecer:
   - peça à TI para liberar a comunicação entre o seu notebook e a rede do laboratório; ou
   - plano B: um túnel público temporário, por exemplo `cloudflared tunnel --url http://localhost:5000` (gera um endereço `https://….trycloudflare.com`), que só depende de internet, e o laboratório tem.

## 3. Durante o evento

- Telão: abra `http://localhost:5000/placar` (tela cheia, atualiza a cada 3 s).
- Aluno perdeu o cookie e não consegue voltar ao apelido? `flask --app app liberar NOME` (mantém os pontos; o próximo login com esse nome assume a conta).
- Apelido repetido: o servidor recusa, o que evita duas pessoas com o mesmo puzzle.
- Errou a flag: espera de 3 s antes da próxima tentativa (aplicada no servidor, por jogador e por nível).
- Antes de cada turma: `flask --app app zerar`.

## 4. Pontuação

Nível 1 (César) 100 · Nível 2 (Vigenère) 200 · Nível 3 (RSA pequeno) 300. Desempate pelo horário do último acerto.

## 5. Referência

`referencia/ataques.py` tem as soluções completas (o código que os alunos montam nos slides). Foi testado contra 400 apelidos diferentes, nos três níveis, sem falhas.

## Segurança

As flags são conferidas só no servidor e nunca vão para o navegador. O segredo fica em `secret.key`. É um servidor de sala de aula: não o exponha na internet além do tempo do evento.

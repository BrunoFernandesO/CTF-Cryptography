# Conteúdo dos slides (exportado do PowerPoint · 37 slides · 21/10/2026)

Fonte da verdade: o arquivo PowerPoint `Criptografia na Pratica - oficina.pptx` (decisão de 21/10: o deck passou a ser editado em PowerPoint; o artefato do tipo Slides ficou na versão 24 e está desatualizado).
Cada slide traz o texto visível e as notas do apresentador. Nos slides de código, `???` marca o TODO que os alunos completam; as soluções estão nas notas.
Em todos os slides, exceto a capa: "by Axion" e WiT no topo; rodapé "produzido por: BRUNO FERNANDES ORTEGA" e "page NN" (omitidos abaixo).
Imagens reais: foto de Bruno (slide 3), história (slides 8, 9 e 10). Ilustrações próprias (desenhadas em 25/10, no visual Axion): disco de cifra com k = 3 (slide 14) e cadeado aberto → caixa trancada → chave, numerados 1 a 3 (slide 31). Espaço reservado que continua: QR de contatos (37). QR codes reais: slide 16 (caderno do Colab) e slide 35 (site do CTF).


## Abertura: quem sou eu e como vamos trabalhar.

### Slide 1 · `cover`
**Texto no slide:**
- Criptografia
- Workshop
- na Prática
- Matemática e Python do Zero ao RSA
- palestrante: BRUNO FERNANDES ORTEGA
- ROD PXQGR
- Você consegue ler isto?

**Notas do apresentador:** Abertura. Antes de falar qualquer coisa, deixe ROD PXQGR projetado e pergunte se alguém consegue ler. É uma cifra de César com deslocamento 3 (OLA MUNDO). Deixe a turma tentar por um minuto: a resposta vira o gancho para a matemática do dia 1.

### Slide 2 · `combinados`
**Texto no slide:**
- Combinados da turma
- ANTES DE COMEÇAR
- 01
- Pode interromper
- Dúvida? Fala na hora.
- 02
- Pode errar
- Erro de código é normal.
- 03
- Pode rir
- Piada ruim? Ria de mim.

**Notas do apresentador:** Tom: descontraído desde o primeiro minuto, em 1 minuto. Leia os três combinados em voz leve e siga para o conteúdo, sem dinâmica de apresentação.

### Slide 3 · `quem-sou-eu`
**Texto no slide:**
- Quem sou eu
- PRAZER
- Bruno Fernandes Ortega
- Estudante de Engenharia de Software · UniCesumar · Axion
- [Como entrei em Engenharia de Software]
- [Minha paixão por matemática e programação]
- [Por que escolhi criptografia]
- NASA Space Apps Challenge - 2025

**Notas do apresentador:** Máximo de 5 minutos. Os três itens em verde são lembretes para você preencher com a sua história: como chegou à Engenharia de Software, a paixão por matemática e programação e o motivo de ter escolhido este tema. O QR code com seus contatos fica no último slide, para ninguém olhar o celular agora.

### Slide 4 · `plano`
**Texto no slide:**
- O plano dos dois dias
- ROTEIRO
- DIA 1 · 26/10
- Do bilhete ao Vigenère
- Introdução e um pouco de história
- Tipos de criptografia
- César: matemática, código e ataque
- Vigenère: matemática e código
- CTF: nível 1 (César)
- DIA 2 · 27/10
- Quebrar coisas e o RSA
- Quebrando o Vigenère em Python
- Euclides e inverso modular
- RSA do zero, em Python
- Quebrando um RSA pequeno
- CTF final: níveis 2 e 3
- 3h30 por dia, com uma pausa no meio.

**Notas do apresentador:** Dia 1: abertura (10 min), intro e história (25), tipos (10), César com Python, nível 1 do CTF e automação do ataque (85), pausa (15), Vigenère (55; se faltar tempo, entregue o vigenere() pronto). Dia 2: aquecimento de 2 min e quebrar Vigenère, com os dois slides do índice de coincidência (49), Euclides sem a prova de Euler (25), pausa (15), RSA (75), CTF final (25), RSA real e encerramento (20): 209 de 210 min. Se ainda apertar: entregue o loop do IC pronto e faça o ataque ao RSA como demonstração sua. Ajuste o texto da pausa se o evento tiver coffee break de verdade.


## Introdução e história da criptografia.

### Slide 5 · `etimologia`
**Texto no slide:**
- O que é criptografia?
- PALAVRA
- kryptós + gráphein
- oculto + escrever = escrita oculta
- Do grego antigo.
- Criptografia
- Esconder a mensagem.
- Criptoanálise
- Quebrar a mensagem.
- Criptologia
- Os dois lados juntos.

**Notas do apresentador:** Rápido: kryptós quer dizer oculto, gráphein quer dizer escrever. Quem esconde é o criptógrafo, quem quebra é o criptoanalista. Hoje vamos fazer os dois papéis: primeiro cifrar, depois atacar a própria cifra.

### Slide 6 · `bilhete`
**Texto no slide:**
- Imagine um bilhete
- ANALOGIA
- Você
- Colega 1
- Colega 2
- Colega 3
- Destino
- Quem pode ler o bilhete no caminho?
- Internet = vários “colegas” no caminho (roteadores)
- Qualquer um pode abrir e ler
- Criptografia = o envelope

**Notas do apresentador:** Exemplo falado, 1 minuto, sem atividade: lembre da época em que bilhetes passavam de mão em mão na sala e qualquer um no caminho podia abrir e ler. Faça a ponte: é assim que os dados viajam pela internet, passando por vários intermediários, e é por isso que precisamos de criptografia. O envelope é a criptografia.

### Slide 7 · `origem`
**Texto no slide:**
- Por que isso nasceu?
- ORIGEM
- Guerra
- Ordens que o inimigo não lê
- Diplomacia
- Segredos de Estado
- Comércio
- Rotas, preços, receitas
- Vida pessoal
- Cartas de amor e fofoca
- Segredo + mensageiro em quem não confio = criptografia.

**Notas do apresentador:** Aqui entra a piada da fofoca: a primeira aplicação de “criptografia” em grupo de mensagem foi esconder a fofoca do grupo. Depois feche com a frase em verde, que resume o problema inteiro.

### Slide 8 · `hist-antiga`
**Texto no slide:**
- Os primeiros truques
- HISTÓRIA · ANTIGUIDADE
- Egito, cerca de 1900 a.C.
- Hieróglifos fora do padrão em tumbas
- Cítala espartana
- Fita enrolada num bastão · uso real debatido
- César, século I a.C.
- Desloca cada letra 3 casas · fonte: Suetônio

**Notas do apresentador:** Três paradas rápidas. Cuidado com as palavras: o Egito é “frequentemente citado” como um dos primeiros exemplos, e o uso real da cítala é debatido pelos historiadores. Já o deslocamento de 3 letras de César é descrito por Suetônio. Vale a piada: “a criptografia mais famosa da Antiguidade foi quebrada por quem tinha uma tarde livre”.

### Slide 9 · `hist-medieval`
**Texto no slide:**
- O jogo de gato e rato
- HISTÓRIA · SÉCULOS IX AO XIX
- Al-Kindi, século IX
- Análise de frequência · adeus, César
- Vigenère, século XVI
- Vários Césares ao mesmo tempo · “indecifrável”
- Século XIX
- Kasiski publica o ataque · Babbage chegou antes

**Notas do apresentador:** A lição é o ritmo: alguém inventa uma cifra, alguém aprende a quebrar, alguém inventa uma melhor. Al-Kindi mostra por que o César é fraco, o Vigenère foi a resposta, e Kasiski (antes dele, Babbage, em segredo) mostrou que o Vigenère também cai. É exatamente a ordem em que vamos trabalhar no dia 1.

### Slide 10 · `hist-moderna`
**Texto no slide:**
- Máquinas, computadores e matemática
- HISTÓRIA · SÉCULO XX EM DIANTE
- Enigma
- II Guerra · Bletchley Park · Turing
- 1976 · Diffie–Hellman
- Combinar chave sem se encontrar
- 1977 · RSA
- Rivest · Shamir · Adleman · vamos construir
- 2001 · AES
- Padrão simétrico de hoje

**Notas do apresentador:** Os marcos que importam para o nosso curso: Enigma mostra que cifras mecânicas também caem; 1976 e 1977 resolvem o problema de combinar a chave antes (é o RSA que veremos no dia 2); o AES é o padrão simétrico de hoje. Se a turma curtir história, deixe espaço para perguntas sobre Turing.

### Slide 11 · `por-que-hoje`
**Texto no slide:**
- E por que isso importa agora?
- HOJE
- VOCÊ USA SEM PERCEBER
- O cadeado do navegador (HTTPS)
- Mensageiros como o WhatsApp
- Senhas guardadas pelos sites
- Pagamentos online
- Assinaturas digitais
- Confidencialidade
- Só quem deve ler, lê.
- Integridade
- Ninguém mexeu no meio do caminho.
- Autenticidade
- Quem enviou é quem diz ser.

**Notas do apresentador:** Pergunte quem já usou algum desses hoje (todos). Volte ao bilhete: criptografia é o envelope. As três propriedades à direita são o que queremos de um envelope: ninguém lê, ninguém altera, e sabemos quem mandou. Piada opcional: “se a sua senha é 123456, a criptografia faz o que pode, mas não faz milagre”.


## O mapa dos tipos de criptografia.

### Slide 12 · `tipos`
**Texto no slide:**
- Tipos de criptografia
- MAPA
- Simétrica
- A mesma chave cifra e decifra.
- Hoje: César e Vigenère. Na vida real: AES.
- vamos estudar
- Assimétrica
- Par de chaves: pública cifra, privada decifra.
- Hoje: RSA.
- vamos estudar
- Hash
- Resumo de tamanho fixo, sem volta.
- Exemplo: SHA-256.
- fica de bônus

**Notas do apresentador:** Aponte o que vamos estudar: César e Vigenère são cifras simétricas clássicas (e fracas), e o RSA é assimétrico. Hash fica de fora, a não ser que sobre tempo. Sistemas reais combinam os três tipos: no HTTPS, por exemplo, a assimétrica ajuda a combinar uma chave, a simétrica protege os dados e os hashes garantem a integridade.

### Slide 13 · `kerckhoffs`
**Texto no slide:**
- Princípio de Kerckhoffs
- A segurança tem que estar na chave, não em esconder como a cifra funciona.
- Segurança por obscuridade não é segurança: é torcida.

**Notas do apresentador:** É por isso que quebrar as cifras em aula vale como estudo: todo o método é público, só a chave é secreta. Algoritmos como AES e RSA são abertos e estudados há décadas. Se um ataque funciona sabendo o método, a cifra é fraca.


## César: ideia, matemática e Python.

### Slide 14 · `caesar-ideia`
**Texto no slide:**
- César: a ideia
- DIA 1 · CÉSAR
- TEXTO ORIGINAL
- A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
- CIFRA, COM K = 3
- D E F G H I J K L M N O P Q R S T U V W X Y Z A B C
- OLA MUNDO → ROD PXQGR
- Gira o alfabeto k casas
- Quem sabe o k, desfaz
- Quem não sabe: 25 tentativas

**Notas do apresentador:** Volte à mensagem da capa: ROD PXQGR é OLA MUNDO com k = 3. Mostre com o dedo cada letra “andando” 3 casas. Pergunte: quantas chaves existem? (25 úteis.) Deixe essa pergunta no ar, porque ela vira o ataque mais tarde.

### Slide 15 · `caesar-math`
**Texto no slide:**
- A matemática por trás
- DIA 1 · CÉSAR
- Cada letra vira um número: A = 0, B = 1, … Z = 25.
- C = (P + k) mod 26
- P = (C − k) mod 26
- Exemplo: O = 14, então (14 + 3) mod 26 = 17, que é R.
- mod é o resto da divisão
- Como um relógio: depois do 25 a gente volta pro 0.
- Z = 25, então (25 + 3) mod 26 = 2, que é C

**Notas do apresentador:** Esta é a ideia central que será reutilizada no Vigenère e no RSA: aritmética modular. Use o relógio como analogia (13h é 1h da tarde). Faça uma conta no quadro com a turma antes de passar adiante: pergunte quanto é (20 + 10) mod 26. Resposta: 4, a letra E.

### Slide 16 · `colab`
**Texto no slide:**
- Abra o caderno do Colab
- DIA 1 · MÃOS NO CÓDIGO
- No computador do laboratório, digite:
- brunofernandeso.pythonanywhere.com/colab
- 1
- Arquivo → Salvar uma cópia no Drive
- 2
- Shift + Enter roda cada célula
- 3
- Célula Conferir: ✓ ou o erro
- Ou aponte a câmera
- do celular

**Notas do apresentador:** Antes de qualquer código, todos abrem o caderno do aluno. Nos computadores do laboratório: digitar brunofernandeso.pythonanywhere.com/colab no navegador (o servidor do CTF redireciona para o caderno). O QR é para quem quiser abrir no celular. Peça que façam Arquivo → Salvar uma cópia no Drive antes de escrever qualquer coisa: sem isso, o trabalho some ao fechar a aba e não sobra nada para o Dia 2. No caderno, o ??? dos slides aparece como None com # TODO; cada exercício tem uma célula Conferir que responde ✓ ou mostra o que saiu. Shift + Enter roda a célula e passa para a próxima. Se o Colab pedir login, é a conta Google do próprio aluno. Tempo: 3 minutos, circulando pela sala.

### Slide 17 · `python-tour`
**Texto no slide:**
- Python em 5 minutos
- DIA 1 · PARA QUEM VEM DE C OU JAVA
- | C / Java | Python
- | (int) c | ord(c)
- | (char) n | chr(n)
- | for (i = 0; i < n; i++) | for i in range(n):
- | chaves { } delimitam blocos | a indentação delimita blocos
- | -3 % 26 dá -3 | -3 % 26 dá 23
- | int pode estourar | inteiros sem limite de tamanho
- | declarar tipos | não precisa declarar

**Notas do apresentador:** Só o que vamos usar hoje. Se você é da turma de C ou Java, a pegadinha mais importante é o %: em C e Java, -3 % 26 dá -3; em Python dá 23, que é o que a matemática modular precisa. ord e chr fazem o papel do cast entre char e int. A indentação substitui as chaves. Abra o Colab e mostre cada linha rodando em uma célula. Aqui é um bom momento para admitir que você também está aprendendo Python, se quiser. O caderno já foi aberto no slide anterior: rode as linhas da tabela em células do Colab.

### Slide 18 · `caesar-codigo`
**Texto no slide:**
- Sua vez: complete a função
- DIA 1 · CÉSAR EM PYTHON
- def cesar(texto, k):
- resultado = ""
- for c in texto.upper():
- if c.isalpha():
- n = ord(c) - ord("A") # A = 0 ... Z = 25
- n = ??? # TODO: some k e use mod 26
- resultado += chr(n + ord("A"))
- else:
- resultado += c
- return resultado
- Teste
- cesar("OLA MUNDO", 3)
- → ROD PXQGR

**Notas do apresentador:** Solução da linha do TODO: n = (n + k) % 26. Deixe 5 a 8 minutos para as duplas tentarem antes de mostrar. Dica para decifrar: é cifrar com -k, então cesar(texto, -3). Aviso: acentos quebram a função (ord de “Á” sai do intervalo), então os textos do exercício vêm sem acento. No Colab, entregue a célula já com o esqueleto e o TODO.

### Slide 19 · `caesar-ataque`
**Texto no slide:**
- Quebrando o César: sua vez
- DIA 1 · ATACANDO
- 25 chaves úteis: teste todas e leia o resultado.
- msg = "[cole a mensagem cifrada]"
- for k in range(1, 26):
- print(k, ???) # TODO: decifre msg com k
- NÍVEL 1 DO CTF · 10 MINUTOS
- Resolva o seu puzzle com o código que você escreveu.
- Lição: poucas chaves, pouco segredo.

**Notas do apresentador:** Solução do TODO: cesar(msg, -k), ou seja, decifrar é cifrar com o deslocamento negativo. Antes disso, apresente o site do CTF: cada aluno escolhe um apelido e recebe o próprio puzzle (k diferente para cada um), então copiar do colega não adianta; o que vale é rodar o próprio código. Deixe uns 10 minutos. Quando alguém acertar, pergunte como soube: “porque parecia português” é exatamente a ideia que vem no próximo slide, ensinar o computador a reconhecer português. CTF V4: antes de apresentar o site, abra o nível 1 no painel (/organizador no celular). Os outros níveis continuam fechados até terça.

### Slide 20 · `caesar-auto`
**Texto no slide:**
- Ensine o Python a reconhecer português
- DIA 1 · ATACANDO
- def pontuacao(texto):
- return ??? # TODO: conte os A, E e O do texto
- def quebrar_cesar(texto):
- melhor_k = 0
- melhor_pontos = 0
- for k in range(26):
- pontos = pontuacao(cesar(texto, -k))
- if pontos > melhor_pontos:
- melhor_k = k
- melhor_pontos = pontos
- return melhor_k
- Teste
- quebrar_cesar(cesar(
- "O CODIGO SECRETO ESTA AQUI",
- 7))
- → 7

**Notas do apresentador:** Solução do TODO: texto.count("A") + texto.count("E") + texto.count("O"). A ideia: em português, A, E e O são as letras mais comuns; o deslocamento certo é o que faz o texto decifrado ter mais A, E e O. A função quebrar_cesar já vem pronta, mas vale ler com a turma: guarda o melhor k e a melhor pontuação (como num máximo em C ou Java). Esta função será reaproveitada amanhã para quebrar o Vigenère, então peça para guardarem o arquivo. Funciona bem em textos de umas dezenas de letras ou mais. Se o tempo apertar, entregue o quebrar_cesar pronto e só discuta a pontuação.


## Vigenère: ideia, código e como quebrar.

### Slide 21 · `vigenere`
**Texto no slide:**
- Vigenère: um César em crise
- DIA 1 · VIGENÈRE
- Ci = (Pi + K[i mod m]) mod 26
- Texto: ATTACKATDAWN
- Chave: LEMONLEMONLE
- Cifra: LXFOPVEFRNHR
- Palavra-chave no lugar de um k
- Cada letra, um deslocamento · m = tamanho da chave (LEMON: m = 5)

**Notas do apresentador:** Exemplo clássico em inglês (ATTACKATDAWN com chave LEMON); nos exercícios o texto estará em português, sem acento. Mostre a primeira letra: A + L (11) = L; a segunda: T + E (4) = X. Cada coluna da chave é um César diferente, e é por isso que a frequência das letras fica espalhada. Piada: o César precisou de uma crise de identidade para virar Vigenère.

### Slide 22 · `vigenere-codigo`
**Texto no slide:**
- Mesma ideia, uma lista de chaves
- DIA 1 · VIGENÈRE EM PYTHON
- def vigenere(texto, chave):
- resultado = ""
- i = 0 # posição na chave
- for c in texto.upper():
- if c.isalpha():
- k = ord(chave[i % len(chave)]) - ord("A")
- resultado += ??? # TODO: reaproveite o cesar()
- i += 1
- else:
- resultado += c
- return resultado
- Teste
- vigenere("ATTACKATDAWN",
- "LEMON")
- → LXFOPVEFRNHR

**Notas do apresentador:** Solução do TODO: resultado += cesar(c, k). A graça é reaproveitar a função do César letra por letra: o Vigenère é um César cujo k muda a cada letra. O índice i só avança nas letras, para espaços e pontuação não consumirem a chave. A chave deve estar em maiúsculas e sem acento.

### Slide 23 · `vigenere-ataque`
**Texto no slide:**
- Como quebrar o Vigenère
- DIA 1 · ATACANDO
- 1
- Descobrir o tamanho da chave
- Kasiski ou índice de coincidência
- 2
- Separar em colunas
- m Césares embaralhados
- 3
- Olhar as frequências
- A, E, O mandam · 1 letra da chave por coluna
- Limpe o texto: sem acentos, espaços ou pontuação.

**Notas do apresentador:** Hoje só a ideia, sem código; o código fica para o dia 2. Faça a ligação com o César: se eu soubesse o tamanho da chave, cada coluna seria uma cifra de César, e César a gente já sabe quebrar com frequência. Esse é o fio condutor do ataque.

### Slide 24 · `fim-dia1`
**Texto no slide:**
- Fim do Dia 01.
- Hoje você cifrou e quebrou duas cifras.
- Amanhã: Vigenère em Python, teoria dos números e RSA.
- Pergunta de despedida: qual foi a parte mais confusa?

**Notas do apresentador:** Reserve 5 minutos para a pergunta final: as respostas dizem o que revisar de manhã. Agradeça a energia da turma e lembre o horário de amanhã. Confira se todos salvaram a cópia do caderno do Colab no próprio Drive: amanhã o Vigenère reaproveita as funções de hoje. Antes de sair: Fechar todos no painel do CTF, senão os textos cifrados ficam visíveis à noite. Não zere o CTF.


## Dia 2: índice de coincidência e quebra do Vigenère em Python.

### Slide 25 · `abertura-dia2`
**Texto no slide:**
- Bom dia! Aquecimento rápido
- DIA 2
- 1
- Por que o César cai em, no máximo, 25 tentativas?
- 2
- O que o Vigenère esconde que o César não esconde?
- 3
- Qual é o primeiro passo para quebrar o Vigenère?
- Respostas em voz alta, sem vergonha. Chute vale.

**Notas do apresentador:** Aquecimento de 2 minutos (corte combinado para caber o índice de coincidência): leia as três perguntas e ouça duas ou três respostas, sem discutir cada uma. Respostas: 1) porque só há 25 deslocamentos úteis, então a força bruta resolve; 2) a frequência das letras, que fica espalhada entre várias cifras de César; 3) descobrir o tamanho da chave. Use a pergunta que a turma errar como guia do que reforçar antes de continuar. Logo depois, peça que abram a cópia do caderno salva ontem e rodem a primeira célula e as funções do Dia 1; quem não terminou ou perdeu a cópia roda só a célula Plano B, que carrega tudo pronto.

### Slide 26 · `ic-ideia`
**Texto no slide:**
- Índice de coincidência
- DIA 2 · A MATEMÁTICA DO ATAQUE
- Sorteie duas letras do texto.
- IC = a chance de saírem iguais
- IC = Σ ni(ni − 1) / N(N − 1)
- ni: quantas vezes a letra i aparece
- N: total de letras do texto
- BANANA: A = 3, N = 2, B = 1
- (3·2 + 2·1 + 1·0) / (6·5) = 8/30 ≈ 0,27
- Português
- ≈ 0,07 a 0,08
- A, E e O se repetem muito
- Texto embaralhado
- 1/26 ≈ 0,038
- 26 letras igualmente prováveis

**Notas do apresentador:** Novo slide (3 a 4 minutos). A ideia: sorteie duas letras do texto, sem reposição; o IC é a probabilidade de saírem iguais. A fórmula conta isso: a letra i aparece nᵢ vezes, então há nᵢ(nᵢ − 1) jeitos de sortear duas cópias dela (em ordem), de um total de N(N − 1) sorteios. Somando sobre as 26 letras, sai IC = Σ nᵢ(nᵢ − 1) / N(N − 1). Exemplo BANANA: A = 3, N = 2, B = 1, então (3·2 + 2·1 + 1·0) / (6·5) = 8/30 ≈ 0,267 (é o mesmo valor que a célula Conferir do caderno espera). Para textos longos, nᵢ(nᵢ − 1)/N(N − 1) ≈ (nᵢ/N)², então IC ≈ Σ pᵢ², a soma dos quadrados das frequências. Texto embaralhado: as 26 letras com a mesma chance, Σ (1/26)² = 26 · (1/26)² = 1/26 ≈ 0,038. Português: as frequências são desiguais (nos nossos textos, E ≈ 15%, A ≈ 13,5%, S ≈ 10%, O ≈ 8%), e quadrados de números grandes pesam muito: o IC dos textos do CTF e do caderno é 0,079. Na literatura, o português fica perto de 0,07 a 0,08. Mensagem para guardar: o IC mede o quanto um texto é desigual nas letras; português é desigual, ruído é uniforme.

### Slide 27 · `ic-tamanho`
**Texto no slide:**
- Por que o IC acha o tamanho
- DIA 2 · A MATEMÁTICA DO ATAQUE
- César só troca o nome das letras
- Contagens iguais → IC igual
- m certo ou múltiplo
- Coluna = um César · IC ≈ 0,08
- Qualquer outro m
- Colunas misturadas · IC mais baixo
- IC médio das colunas · exemplo do caderno (chave SOL)
- Regra: maior IC → menor m a menos de 0,01 dele

**Notas do apresentador:** Novo slide (3 a 4 minutos). O argumento central: uma cifra de César só troca o nome das letras; as contagens continuam as mesmas, então o IC não muda. Se m é o tamanho certo, a coluna texto[i::m] só tem letras cifradas com a mesma letra da chave: é um César de um pedaço de português, e o IC fica alto. Nos 400 puzzles do CTF, o m certo (ou um múltiplo dele) deu entre 0,076 e 0,083. Se m está errado, cada coluna mistura letras deslocadas por valores diferentes: as frequências se espalham e o IC desce em direção a 1/26. Qualquer outro m deu entre 0,039 e 0,067. Os múltiplos também dão IC alto (com SOL, m = 6 gera colunas S, O, L, S, O, L). Os divisores dão um meio-termo: com chave de 6 letras, m = 3 mistura só dois deslocamentos por coluna e sobe para perto de 0,06 a 0,067. É por isso que a regra é ‘o menor m a menos de 0,01 do maior IC’, e não ‘o primeiro que parece alto’. O gráfico é a tabela do caderno (texto de exemplo, chave SOL): 3 e 6 se destacam; 7 dá 0,058 por acaso, ainda longe do máximo. A regra acertou 400 de 400 puzzles; a menor folga entre um m errado e o máximo foi 0,016.

### Slide 28 · `vigenere-tamanho`
**Texto no slide:**
- Passo 1: o tamanho da chave
- DIA 2 · VIGENÈRE EM PYTHON
- from collections import Counter
- def ic(s):
- n = len(s)
- return sum(v * (v - 1) for v in Counter(s).values()) / (n * (n - 1))
- texto = "[cole o texto cifrado, sem espaços]"
- for m in range(2, 9):
- colunas = ??? # TODO: m colunas (dica: texto[i::m])
- media = sum(ic(c) for c in colunas) / m
- print(m, round(media, 4))
- Para cada m: IC médio das colunas
- m certo (ou múltiplo): IC mais alto
- Português ≈ 0,07 · embaralhado ≈ 0,04

**Notas do apresentador:** Solução do TODO: [texto[i::m] for i in range(m)]. Se a turma estranhar a list comprehension, escreva o equivalente em loop: colunas = []; for i in range(m): colunas.append(texto[i::m]). A função ic() já vem pronta (é o índice de coincidência: a chance de duas letras sorteadas do texto serem iguais); o foco dos alunos é separar as colunas e olhar o resultado. Em português o IC fica perto de 0,07; em texto embaralhado, perto de 0,04 (1/26). Múltiplos do tamanho real da chave também dão IC alto: se a chave tem 3 letras, m = 6 também aparece bem. Regra para ler a tabela: ache o maior IC (perto de 0,08) e escolha o menor m que fica a menos de 0,01 dele. Valores intermediários, perto de 0,06, não contam: aparecem quando m divide o tamanho real (chave de 6 letras faz o m = 3 subir um pouco) e enganam quem pega o primeiro valor que parece alto. Testado em 400 puzzles do CTF: essa regra acerta todos. Se o tempo apertar, entregue também o loop pronto e só interprete a tabela. A teoria do índice de coincidência está nos dois slides anteriores; aqui o foco é o código e a leitura da tabela.

### Slide 29 · `vigenere-colunas`
**Texto no slide:**
- Passo 2: a chave, coluna por coluna
- DIA 2 · VIGENÈRE EM PYTHON
- m = 5 # o tamanho que você descobriu
- chave = ""
- for i in range(m):
- coluna = texto[i::m]
- k = quebrar_cesar(coluna) # o ataque ao César de ontem!
- chave += ??? # TODO: transforme k na letra da chave
- print(chave)
- Cada coluna é um César
- quebrar_cesar devolve o deslocamento k
- Chave repetida (SOLSOL)? A verdadeira é a menor

**Notas do apresentador:** Solução do TODO: chr(k + ord("A")), o inverso do que fizemos para transformar letra em número. O ponto central: se a gente sabe o tamanho m, cada coluna do texto foi cifrada com um único deslocamento, ou seja, é um César; e César a gente já quebra com quebrar_cesar. Exercício: pegue o texto do nível 2 do CTF (remova os espaços), descubra m no passo anterior, rode este loop e envie FLAG{CHAVE}. Se o resultado vier repetido, como SOLSOL, a chave verdadeira é SOL. Bônus para quem terminar: decifrar o texto inteiro com vigenere() usando a chave inversa (26 - k em cada letra). CTF V4: abra o nível 2 no painel agora; ele aparece sozinho na tela dos alunos em até 10 s.


## Dia 2: RSA, do zero ao ataque.

### Slide 30 · `euclides`
**Texto no slide:**
- Dois truques para o RSA
- DIA 2 · MATEMÁTICA
- Euclides: o mdc
- def mdc(a, b):
- while b:
- a, b = b, a % b
- return a
- mdc(48, 18) # 6
- Inverso modular
- pow(17, -1, 3120) # 2753
- 17 * 2753 % 3120 # 1
- d é o inverso de e quando e · d deixa resto 1.
- mdc(a, n) = 1 ⇒ aφ(n) ≡ 1 (mod n)
- Euler: é o que faz decifrar desfazer cifrar.

**Notas do apresentador:** Primeiro peça para escreverem o mdc à mão; depois mostre que o Python já tem pow(a, -1, n) para o inverso modular (precisa de Python 3.8 ou mais novo). Pule a prova do teorema de Euler (corte combinado para caber o índice de coincidência); ela está no guia de estudo para quem perguntar. A única coisa que precisam levar é: se mdc(e, φ) = 1, existe um d tal que e · d deixa resto 1 módulo φ.

### Slide 31 · `rsa-ideia`
**Texto no slide:**
- RSA: o cadeado público
- DIA 2 · RSA
- 1
- Publique o cadeado aberto (chave pública)
- 2
- Qualquer um fecha a caixa
- 3
- Só você abre (chave privada)
- Virada dos anos 70: trocar segredos sem se encontrar.

**Notas do apresentador:** Volte ao bilhete do dia 1: com cifras simétricas, os dois lados precisam combinar a chave antes. No RSA, você distribui o cadeado (chave pública) para o mundo e guarda a chave só com você. A segurança vem de um problema matemático difícil: multiplicar dois primos grandes é fácil, mas fatorar o resultado é muito difícil.

### Slide 32 · `rsa-chaves`
**Texto no slide:**
- RSA: fabricando as chaves
- DIA 2 · RSA
- 1. Escolha dois primos grandes, p e q
- 2. n = p · q
- 3. φ(n) = (p − 1)(q − 1)
- 4. Escolha e com mdc(e, φ(n)) = 1
- 5. d = inverso de e módulo φ(n)
- Chave pública: (n, e). Chave privada: (n, d).
- EXEMPLO PEQUENO
- p = 61, q = 53
- n = 3233, φ(n) = 3120
- e = 17, d = 2753
- m = 65 → c = 6517 mod 3233 = 2790
- 27902753 mod 3233 = 65

**Notas do apresentador:** Faça o exemplo à mão com a turma, com calculadora: 61 × 53 = 3233; 60 × 52 = 3120; 17 × 2753 deixa resto 1 na divisão por 3120. Cifre o 65 e mostre que decifrar traz o 65 de volta. A parte pesada das contas (as potências) fica para o Python no próximo slide.

### Slide 33 · `rsa-codigo`
**Texto no slide:**
- RSA em poucas linhas
- DIA 2 · RSA EM PYTHON
- p, q = 61, 53
- n = p * q # 3233
- phi = (p - 1) * (q - 1) # 3120
- e = 17
- d = pow(e, -1, phi) # 2753: a chave privada
- c = pow(65, e, n) # cifrar o 65: dá 2790
- m = pow(c, d, n) # decifrar: volta o 65
- Troque p e q por primos maiores e veja o que muda.

**Notas do apresentador:** Cada linha corresponde a um passo do slide anterior; pow(a, b, n) faz a exponenciação modular de forma eficiente, e pow(e, -1, phi) calcula o inverso. As mensagens precisam ser números menores que n: para texto, é preciso converter cada caractere em número, o que fica como bônus. Peça que cada dupla escolha seus próprios p e q (primos pequenos) e cifre um número.

### Slide 34 · `rsa-ataque`
**Texto no slide:**
- Quebrando o RSA: fatorar n
- DIA 2 · ATACANDO
- Fatorou n = p · q? Recalcula φ(n) e acha d.
- def fatorar(n):
- f = 2
- while ???: # TODO: enquanto f NÃO divide n
- f += 1
- return f, n // f
- p, q = fatorar(n)
- phi = ??? # TODO: φ(n)
- d = pow(e, -1, phi)
- m = pow(c, d, n)
- print(m)
- Por que o RSA de livro é inseguro
- Sem padding, é determinístico
- É maleável: dá para mexer no cifrado
- Chaves pequenas são fatoráveis
- n = 3233: instantâneo · 2048 bits (≈ 617 dígitos): inviável.

**Notas do apresentador:** Soluções dos TODO: while n % f != 0 e phi = (p - 1) * (q - 1). É o nível 3 do CTF: o aluno cola n, e e c do puzzle dele, fatora, calcula d com pow(e, -1, phi) e decifra com pow(c, d, n); a flag é FLAG{m}. Cada aluno tem n diferente. Se o tempo estiver curto, faça a fatoração como demonstração sua: gere um n com primos de 4 a 6 dígitos, mostre a divisão sucessiva e meça o tempo à medida que n cresce, para a turma sentir por que o tamanho da chave importa. Com 2048 bits (cerca de 617 dígitos), fatorar não é viável com os métodos conhecidos. CTF V4: abra o nível 3 no painel antes do exercício.

### Slide 35 · `ctf-final`
**Texto no slide:**
- CTF: use o seu código
- DIA 2 · DESAFIO FINAL
- Nível 1
- César
- 100 pts
- Nível 2
- Vigenère
- 200 pts
- Nível 3
- RSA pequeno
- 300 pts
- Seu apelido gera o seu puzzle
- Resposta no formato FLAG{...}
- Vale o código que você escreveu
- Placar no telão · 25 minutos
- brunofernandeso.
- pythonanywhere.com

**Notas do apresentador:** Cerca de 25 minutos, individual ou em duplas, a critério de cada um. O nível 1 já foi resolvido no fim do dia 1 (quem não fez pode fazer agora). O puzzle depende do apelido, então copiar a resposta do colega não funciona: o que vale é rodar o próprio código. Dicas por nível estão no site. Nível 2: use o código do tamanho da chave e das colunas (quebrar_cesar de ontem); nível 3: fatore n e use pow(e, -1, phi). Para os calouros: circule pela sala, incentive pedir dica, e mostre o placar parcial no telão no meio do tempo. Fechamento: congratule quem fez cada nível e mostre a solução do nível 3 ao vivo se ninguém chegar lá. O QR abre o site do CTF; o placar do telão fica em /placar. O fim do caderno do Colab tem uma tabela dizendo qual célula usar em cada nível e o formato de cada flag. No nível 2, lembre a regra da tabela do IC: ache o maior valor e escolha o menor m que chega perto dele. CTF V4: Abrir todos no painel (o nível 1 volta para quem não fez ontem).

### Slide 36 · `rsa-real`
**Texto no slide:**
- Regra de ouro
- Na vida real, use biblioteca.
- Implementar a sua: ótimo para aprender, péssimo para produção.

**Notas do apresentador:** Mensagem final do conteúdo técnico. Tudo o que fizemos hoje é didático: serve para entender como a coisa funciona, não para proteger dados reais. Em projetos de verdade, use bibliotecas consolidadas e deixe a escolha de algoritmos e parâmetros para quem estuda isso profissionalmente. Detalhes para falar: o RSA de verdade usa chaves de 2048 bits ou mais, padding (OAEP) e, em geral, só troca uma chave do AES.


## Encerramento e contatos.

### Slide 37 · `close`
**Texto no slide:**
- Perguntas?
- [QR CODE: LinkedIn e link da bio]
- CryptoHack
- Desafios interativos e gratuitos.
- Cryptography I
- Curso de Dan Boneh, de Stanford.
- Cryptopals
- Exercícios práticos de ataques.
- Valeu pela energia, pessoal!
- [seu LinkedIn]
- [seu Instagram]
- [seu e-mail]

**Notas do apresentador:** Deixe este slide aberto durante as perguntas. O QR code leva a uma única página com seu LinkedIn (e, se você quiser, o Instagram). Tire uma foto da turma antes de sair, se todos concordarem. Os três recursos: CryptoHack (desafios gratuitos), o curso Cryptography I de Dan Boneh e os desafios do Cryptopals. Antes das perguntas: Fechar todos no painel do CTF.

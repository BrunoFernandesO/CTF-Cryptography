// Trilha de circuito: um nó por nível, aceso em lima quando resolvido (aluno e telão) ou aberto (painel do organizador).
const NIVEIS = [
  { id: 1, nome: 'César' },
  { id: 2, nome: 'Vigenère' },
  { id: 3, nome: 'RSA' },
];

function trilhaSVG(resolvidos, { gap = 44, r = 7, rotulos = false, sim = 'resolvido', nao = 'pendente' } = {}) {
  const feitos = new Set(resolvidos);
  const pad = rotulos ? 26 : r + 2;
  const w = pad * 2 + gap * (NIVEIS.length - 1);
  const h = rotulos ? r * 2 + 22 : r * 2 + 4;
  const cy = r + 2;
  const x = i => pad + i * gap;
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('width', w);
  svg.setAttribute('height', h);
  svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', NIVEIS.map(n => `${n.nome} ${feitos.has(n.id) ? sim : nao}`).join(', '));
  const wire = document.createElementNS(ns, 'line');
  wire.setAttribute('class', 'wire');
  wire.setAttribute('x1', x(0)); wire.setAttribute('x2', x(NIVEIS.length - 1));
  wire.setAttribute('y1', cy); wire.setAttribute('y2', cy);
  svg.append(wire);
  NIVEIS.forEach((n, i) => {
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('class', 'node' + (feitos.has(n.id) ? ' on' : ''));
    c.setAttribute('cx', x(i)); c.setAttribute('cy', cy); c.setAttribute('r', r);
    svg.append(c);
    if (rotulos) {
      const t = document.createElementNS(ns, 'text');
      t.setAttribute('x', x(i)); t.setAttribute('y', cy + r + 16);
      t.setAttribute('text-anchor', 'middle');
      if (feitos.has(n.id)) t.setAttribute('class', 'on');
      t.textContent = n.nome;
      svg.append(t);
    }
  });
  const span = document.createElement('span');
  span.className = 'trail';
  span.append(svg);
  return span;
}

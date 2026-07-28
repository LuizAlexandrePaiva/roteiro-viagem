# Roteiro de viagem

Uma página única para acompanhar uma viagem: linha do tempo dos deslocamentos,
endereços, telefones e avisos. Instala na tela de início do Android e do iPhone
e continua funcionando sem internet — que é justamente quando um roteiro
costuma ser consultado.

Foi escrita para um caso concreto: alguém viaja, e a família em casa quer saber
onde essa pessoa está e como falar com ela. Todo o resto decorre disso.

**Os dados desta página são fictícios.** Nomes, endereços e telefones existem
apenas para demonstrar o formato.

---

## Índice

- [O que tem dentro](#o-que-tem-dentro)
- [Começando](#começando)
- [Publicando](#publicando)
- [Como editar o roteiro](#como-editar-o-roteiro)
- [Trocando o ícone](#trocando-o-ícone)
- [Decisões de projeto](#decisões-de-projeto)
- [Acessibilidade](#acessibilidade)
- [Compatibilidade](#compatibilidade)
- [Estrutura dos arquivos](#estrutura-dos-arquivos)
- [Licença](#licença)

---

## O que tem dentro

**Linha do tempo com trilha contínua.** Cada dia é um bloco; cada parada é uma
etapa ligada à seguinte por um fio vertical que se desenha conforme a página
rola. Marcadores cheios são compromissos com hora marcada — ônibus, aula,
reserva. Marcadores vazados são sugestões, que podem escorregar sem quebrar
nada. A distinção é visual porque é a primeira pergunta de quem lê: o que dá
para atrasar?

**Cartões de local.** Para paradas que exigem decisão, um cartão com endereço,
horário de funcionamento, telefone e link direto para o mapa.

**Barra fixa com seção corrente.** Os dias aparecem como botões com o dia da
semana pequeno e o número grande. O botão da seção em que você está fica
preenchido e desliza sozinho para dentro da vista quando a barra precisa rolar
de lado. Um fio de 2 px na base mostra o progresso de leitura.

**Instalação na tela de início.** Um cartão discreto oferece a instalação. No
Android usa o convite nativo do Chrome; no iPhone, onde não existe instalação
programática, vira a instrução exata do menu Compartilhar. Some sozinho depois
de instalado e continua acessível por um botão no rodapé.

**Funciona sem internet.** Um *service worker* guarda a página e os ícones.
Páginas são buscadas da rede primeiro, para nunca travar numa versão antiga; o
cache entra quando o sinal some.

**Imprime bem.** Estilos de impressão escondem barra, links de mapa e animações,
e evitam quebrar seções ao meio.

---

## Começando

Não há dependências, empacotador nem etapa de build. Clone e abra:

```bash
git clone https://github.com/<usuario>/roteiro-viagem.git
cd roteiro-viagem
python3 -m http.server 8000
```

E acesse `http://localhost:8000`.

> Abrir o `index.html` com duplo clique também mostra a página, mas o *service
> worker* e a instalação exigem `http://localhost` ou HTTPS.

Edite o `index.html` e recarregue. É isso.

---

## Publicando

### Netlify

Arraste a pasta em [app.netlify.com/drop](https://app.netlify.com/drop). Os
arquivos `_headers` e `_redirects` já vão junto e cuidam do tipo MIME do
manifest e do cache do *service worker*.

### GitHub Pages

Ative Pages apontando para a branch principal, pasta raiz. Funciona, com duas
ressalvas: o Pages ignora `_headers` e `_redirects`, e o site fica numa
subpasta (`/<repositorio>/`). Nesse caso, ajuste no `manifest.webmanifest`:

```json
"id": "/<repositorio>/",
"start_url": "./",
"scope": "./"
```

### Qualquer outra hospedagem estática

Suba os arquivos da raiz. O único requisito é HTTPS, exigido pelo *service
worker* e pela instalação.

---

## Como editar o roteiro

Tudo mora no `index.html`, em blocos comentados. Não há banco de dados nem
arquivo de configuração: o conteúdo é o próprio HTML.

### Datas da viagem

No início do `<script>`, no fim do arquivo:

```js
var TRIP_START = '2027-03-05T21:00:00-03:00';
var TRIP_END   = '2027-03-07T19:00:00-03:00';
```

Alimentam a contagem regressiva do topo, que troca sozinha para "viagem em
andamento" e depois "viagem concluída".

### Um dia

Duplique uma seção `day` inteira. O `id` precisa bater com o `data-sec` do
botão correspondente na barra de navegação.

```html
<section class="day" id="dia-4">
  <div class="wrap">
    <div class="day-head">
      <div class="day-num">08</div>
      <div class="day-meta">
        <h2>Segunda-feira</h2>
        <p>São Paulo → Curitiba</p>
      </div>
    </div>
    <div class="legs">
      <div class="rail"><i></i></div>
      <ol class="steps">
        <!-- etapas aqui -->
      </ol>
    </div>
  </div>
</section>
```

E o botão na barra:

```html
<a href="#dia-4" data-sec="dia-4"><span class="wd">Seg</span><span class="dy">08</span></a>
```

### Uma etapa

```html
<li class="leg fixed rv">
  <div class="t">08h00<small>fixo</small></div>
  <div class="body">
    <h3>Título curto do que acontece</h3>
    <p class="note">Uma ou duas frases com o detalhe prático que importa.</p>
  </div>
</li>
```

| Classe            | Marcador | Quando usar                                  |
| ----------------- | -------- | -------------------------------------------- |
| `leg fixed rv`    | cheio    | hora marcada por terceiros: ônibus, aula      |
| `leg rv`          | vazado   | sugestão, pode escorregar                     |

O `<small>` é texto livre — `fixo`, `sugerido`, `aprox.`, `combinado`. A classe
`rv` liga a aparição suave ao rolar; mantenha-a.

### Um cartão de local

Vai dentro do `<div class="body">` de uma etapa, depois da nota:

```html
<div class="place">
  <div class="ph">
    <div class="pn">Nome do lugar</div>
    <div class="tag">Categoria</div>
  </div>
  <p class="pd">Duas ou três linhas sobre o lugar.</p>
  <dl class="dl">
    <dt>Endereço</dt><dd>Rua Exemplo, 100 — Bairro, Cidade (UF)</dd>
    <dt>Sábado</dt><dd><b>10h às 18h</b></dd>
    <dt>Telefone</dt><dd><a href="tel:+551155550100">(11) 5555-0100</a></dd>
  </dl>
  <a class="maplink" target="_blank" rel="noopener"
     href="https://www.google.com/maps/search/?api=1&amp;query=Rua%20Exemplo%20100">Abrir no mapa →</a>
</div>
```

O endereço do link precisa ir codificado para URL.

### Contatos e avisos

Contatos são linhas de uma tabela; avisos são itens de uma lista `alerts`. Os
dois blocos estão no fim do arquivo, comentados.

---

## Trocando o ícone

O desenho fica no `tools/make-icons.py`. Edite as cores ou o traçado e rode:

```bash
pip install cairosvg
python3 tools/make-icons.py
```

O script regenera os quatro arquivos e imprime a cadeia base64 do ícone do iOS,
que precisa ser colada no `index.html`. O motivo dessa exceção está em
[Decisões de projeto](#decisões-de-projeto).

Se mudar o desenho, mantenha o conteúdo dentro dos 60% centrais: o Android
recorta ícones `maskable` em círculo.

---

## Decisões de projeto

**Um arquivo, sem build.** O HTML carrega CSS e JavaScript embutidos. Um
roteiro de viagem é consultado por dois ou três dias e depois arquivado; ter
que instalar dependências para corrigir um horário na véspera da viagem seria
absurdo. Editar e recarregar é a operação certa para o ciclo de vida deste
projeto. O custo é um arquivo grande — aceitável para uma página só.

**Conteúdo em HTML, não em JSON.** Uma versão orientada a dados seria mais
elegante, mas exigiria renderização em JavaScript, e aí a página deixaria de
existir sem script: nada de impressão limpa, nada de leitura se algo falhar. A
informação precisa estar no documento.

**Rede primeiro para páginas, cache primeiro para o resto.** Um roteiro que
trava numa versão antiga é pior do que um roteiro que demora meio segundo. Já
ícones e fontes não mudam, e ganham vindo do cache.

**O ícone do iOS vai embutido em base64.** O Safari não aceita SVG em
`apple-touch-icon`, e um caminho relativo quebraria se a página fosse aberta
fora da raiz. Custa 8 KB e resolve os dois problemas.

**`beforeinstallprompt` capturado no `<head>`.** O Chrome dispara esse evento
cedo, às vezes antes do fim do corpo da página. Escutá-lo no fim do arquivo
funciona na primeira visita e falha na segunda, quando o *service worker* já
está ativo. Um bloco mínimo no `<head>` guarda o evento; o resto do código o
consome depois.

**Cores conferidas, não escolhidas no olho.** Todos os pares texto/fundo foram
medidos. Texto secundário em 6:1, rótulos pequenos em 8,4:1, separadores de
tabela em 2,5:1. A primeira versão tinha separadores em 1,3:1 — passavam
despercebidos e faziam as linhas se fundirem.

**`:hover` só onde existe ponteiro.** Estados de *hover* ficam dentro de
`@media (hover: hover)`. Sem isso, o toque no celular deixa o realce grudado no
último item tocado.

---

## Acessibilidade

- Marcação semântica: `header`, `nav`, `main`, `section`, listas ordenadas para
  sequências temporais.
- `aria-current` no item de navegação da seção corrente, `aria-label` na
  navegação, `aria-hidden` em elementos decorativos.
- Contraste medido em todos os pares de texto (mínimo 6:1 para texto
  secundário, bem acima dos 4,5:1 da AA).
- Alvos de toque com no mínimo 40 px de altura.
- `prefers-reduced-motion` desliga a trilha animada, as aparições e a rolagem
  suave.
- `scroll-margin-top` nas seções, para o título não parar debaixo da barra fixa.
- Foco visível com `:focus-visible`.
- A página inteira funciona sem JavaScript; só a contagem regressiva, a seção
  corrente e a oferta de instalação dependem dele.

---

## Compatibilidade

| Recurso                        | Chrome/Android | Safari/iOS        | Navegadores de mesa |
| ------------------------------ | -------------- | ----------------- | ------------------- |
| Página, impressão, links       | sim            | sim               | sim                 |
| Instalar na tela de início     | convite nativo | menu Compartilhar | Chrome e Edge       |
| Uso sem internet               | sim            | sim               | sim                 |
| Abrir sem barra do navegador   | sim            | sim               | sim                 |

O conteúdo funciona em qualquer navegador atual. `backdrop-filter` e
`mask-image` degradam sem quebrar o layout.

---

## Estrutura dos arquivos

```
.
├── index.html              página inteira: conteúdo, estilo e comportamento
├── manifest.webmanifest    identidade do aplicativo instalado
├── sw.js                   service worker: uso sem internet
├── favicon.svg             ícone da aba
├── icon-192.png            ícone do Android
├── icon-512.png            ícone do Android e tela de abertura
├── apple-touch-icon.png    ícone do iOS
├── _headers                tipo MIME do manifest, cache do sw (Netlify)
├── _redirects              qualquer caminho entrega a página (Netlify)
└── tools/
    └── make-icons.py       regenera os ícones a partir do SVG
```

---

## Licença

MIT. Veja [LICENSE](LICENSE).

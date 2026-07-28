# Roteiro de Viagem

Aplicação web de página única para documentação e acompanhamento de itinerários
de viagem. Apresenta a sequência de deslocamentos em linha do tempo, reúne
endereços, telefones e avisos operacionais, é instalável na tela de início de
dispositivos Android e iOS e permanece disponível sem conexão com a internet.

![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-informational)
![Sem dependências](https://img.shields.io/badge/depend%C3%AAncias-nenhuma-success)
![PWA instalável](https://img.shields.io/badge/PWA-instal%C3%A1vel-blueviolet)
![HTML, CSS e JavaScript](https://img.shields.io/badge/stack-HTML%20%C2%B7%20CSS%20%C2%B7%20JS-lightgrey)

![Topo da página: título, contagem regressiva para a viagem e três destaques com saída, curso e retorno](docs/preview.png)

> **Aviso.** Todo o conteúdo distribuído neste repositório é fictício. Nomes de
> estabelecimentos, endereços, telefones e datas existem exclusivamente para
> demonstrar o formato da página.

---

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Execução local](#execução-local)
- [Configuração](#configuração)
- [Referência de componentes](#referência-de-componentes)
- [Geração de ícones](#geração-de-ícones)
- [Publicação](#publicação)
- [Arquitetura](#arquitetura)
- [Decisões técnicas](#decisões-técnicas)
- [Acessibilidade](#acessibilidade)
- [Compatibilidade](#compatibilidade)
- [Estrutura de diretórios](#estrutura-de-diretórios)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Visão geral

O projeto atende a um cenário específico: uma pessoa viaja e precisa manter
terceiros — familiares, colegas ou uma equipe — informados sobre sua localização
e sobre os meios de contato disponíveis a cada momento. As decisões de produto e
de engenharia derivam desse cenário.

Duas consequências orientam a implementação. A primeira é que a informação
precisa permanecer acessível em condições adversas de rede, situação frequente
em terminais rodoviários e durante deslocamentos. A segunda é que a hierarquia
visual deve distinguir compromissos com horário determinado de sugestões
flexíveis, pois essa é a informação decisiva para quem acompanha o itinerário à
distância.

---

## Funcionalidades

| Recurso | Descrição |
| --- | --- |
| Linha do tempo | Etapas encadeadas por trilha vertical contínua, com progressão sincronizada à rolagem da página. |
| Classificação de etapas | Marcadores preenchidos indicam compromissos com horário determinado; marcadores vazados indicam sugestões. |
| Cartões de local | Bloco estruturado com endereço, horário de funcionamento, telefone e vínculo para aplicativo de mapas. |
| Navegação com indicação de contexto | Barra fixa com destaque da seção corrente, rolagem horizontal automática e indicador de progresso de leitura. |
| Instalação como aplicativo | Instalação na tela de início em Android e iOS, com fluxos distintos por plataforma. |
| Operação sem conexão | *Service worker* com estratégias diferenciadas por tipo de requisição. |
| Impressão | Folha de estilos dedicada, com supressão de elementos interativos e controle de quebra de página. |

---

## Requisitos

**Para uso e publicação:** nenhum. O projeto não possui dependências de
execução, etapa de compilação ou gerenciador de pacotes.

**Para regeneração dos ícones:** Python 3.8 ou superior e a biblioteca
[CairoSVG](https://cairosvg.org/).

---

## Execução local

```bash
git clone https://github.com/<usuario>/roteiro-viagem.git
cd roteiro-viagem
python3 -m http.server 8000
```

A aplicação fica disponível em `http://localhost:8000`.

A abertura direta do `index.html` pelo sistema de arquivos exibe a página
corretamente, mas não habilita o *service worker* nem o fluxo de instalação, que
exigem origem `http://localhost` ou HTTPS.

---

## Configuração

### Período da viagem

Definido em duas constantes no início do bloco `<script>`, ao final do
`index.html`. Os valores seguem o formato ISO 8601 com deslocamento de fuso
horário.

```js
var TRIP_START = '2027-03-05T21:00:00-03:00';
var TRIP_END   = '2027-03-07T19:00:00-03:00';
```

As constantes alimentam o indicador de estado exibido no cabeçalho, que assume
três formas conforme a data corrente: contagem regressiva, viagem em andamento
ou viagem concluída.

### Identidade da aplicação instalada

Definida em `manifest.webmanifest`.

| Campo | Função |
| --- | --- |
| `name` | Nome exibido na tela de abertura e na lista de aplicativos. |
| `short_name` | Rótulo sob o ícone na tela de início. Recomenda-se no máximo 12 caracteres. |
| `id` | Identificador estável da aplicação. Alterações posteriores produzem instalação duplicada. |
| `start_url`, `scope` | Endereço inicial e escopo de navegação, relativos ao manifesto. |
| `theme_color` | Cor da barra do sistema durante a execução. |
| `background_color` | Cor de fundo da tela de abertura. |

O elemento `<meta name="theme-color">` do `index.html` deve acompanhar o valor
de `theme_color`.

---

## Referência de componentes

O conteúdo reside integralmente no `index.html`, em blocos delimitados por
comentários. Não há camada de dados separada; a justificativa consta em
[Decisões técnicas](#decisões-técnicas).

### Seção de dia

Cada dia do itinerário corresponde a uma seção. O atributo `id` deve
corresponder ao `data-sec` do item equivalente na barra de navegação.

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
        <!-- etapas -->
      </ol>
    </div>
  </div>
</section>
```

Item correspondente na barra de navegação:

```html
<a href="#dia-4" data-sec="dia-4"><span class="wd">Seg</span><span class="dy">08</span></a>
```

### Etapa

```html
<li class="leg fixed rv">
  <div class="t">08h00<small>fixo</small></div>
  <div class="body">
    <h3>Título da etapa</h3>
    <p class="note">Detalhamento operacional em uma ou duas frases.</p>
  </div>
</li>
```

| Classe | Marcador | Aplicação |
| --- | --- | --- |
| `leg fixed rv` | preenchido | Horário determinado por terceiros: transporte, aula, reserva. |
| `leg rv` | vazado | Sugestão sem horário obrigatório. |

O elemento `<small>` aceita texto livre. Os valores em uso na demonstração são
`fixo`, `sugerido`, `aprox.` e `combinado`. A classe `rv` habilita a transição
de entrada e deve ser preservada.

### Cartão de local

Inserido no interior de `<div class="body">`, após o parágrafo de nota.

```html
<div class="place">
  <div class="ph">
    <div class="pn">Nome do estabelecimento</div>
    <div class="tag">Categoria</div>
  </div>
  <p class="pd">Descrição em duas ou três linhas.</p>
  <dl class="dl">
    <dt>Endereço</dt><dd>Rua Exemplo, 100 — Bairro, Cidade (UF)</dd>
    <dt>Sábado</dt><dd><b>10h às 18h</b></dd>
    <dt>Telefone</dt><dd><a href="tel:+551155550100">(11) 5555-0100</a></dd>
  </dl>
  <a class="maplink" target="_blank" rel="noopener"
     href="https://www.google.com/maps/search/?api=1&amp;query=Rua%20Exemplo%20100">Abrir no mapa →</a>
</div>
```

O parâmetro `query` do vínculo para mapas deve estar codificado para URL.

### Contatos

Linhas da tabela `.contacts`. O atributo `href` do vínculo `tel:` deve conter o
número em formato internacional, sem separadores.

```html
<tr>
  <td><span class="who">Nome</span><span class="sub">Função</span></td>
  <td><a class="tel" href="tel:+551155550100"><!-- ícone --><span>(11) 5555-0100</span></a></td>
</tr>
```

### Avisos

Itens da lista `.alerts`. Destinam-se a informações cuja omissão gera
consequência operacional: divergência entre pontos de embarque e desembarque,
janelas de tempo reduzidas, distâncias superiores à esperada.

```html
<li class="rv"><b>Resumo em negrito.</b> Detalhamento.</li>
```

---

## Geração de ícones

O desenho vetorial e as cores são definidos em `tools/make-icons.py`.

```bash
pip install cairosvg
python3 tools/make-icons.py
```

O script produz `favicon.svg`, `icon-192.png`, `icon-512.png` e
`apple-touch-icon.png`, e imprime a representação em base64 do ícone de 180
pixels, que deve substituir o valor do atributo `href` no elemento
`<link rel="apple-touch-icon">` do `index.html`.

Ícones declarados com `purpose: maskable` são recortados em círculo pelo
Android. O conteúdo gráfico deve permanecer dentro dos 60% centrais da área
para evitar truncamento.

---

## Publicação

O requisito único é hospedagem estática com HTTPS, condição necessária para o
*service worker* e para a instalação como aplicativo.

### Netlify

Publicação por transferência do diretório em
[app.netlify.com/drop](https://app.netlify.com/drop) ou por integração contínua
a partir do repositório. Os arquivos `_headers` e `_redirects` são interpretados
automaticamente e definem, respectivamente, o tipo MIME do manifesto e a
política de cache do *service worker*.

### GitHub Pages

Habilitar em *Settings → Pages*, indicando a branch principal e o diretório
raiz. Duas observações se aplicam:

1. Os arquivos `_headers` e `_redirects` são ignorados pela plataforma.
2. O site é servido em subdiretório, o que exige ajuste no manifesto:

```json
"id": "/<repositorio>/",
"start_url": "./",
"scope": "./"
```

### Demais provedores

Transferir os arquivos do diretório raiz. Recomenda-se configurar
`Content-Type: application/manifest+json` para `manifest.webmanifest` e
`Cache-Control: no-cache` para `sw.js`.

---

## Arquitetura

### Estratégia de cache

O *service worker* aplica políticas distintas conforme o tipo de requisição.

| Tipo de requisição | Política | Justificativa |
| --- | --- | --- |
| Navegação (`req.mode === 'navigate'`) | Rede com recurso ao cache | Assegura que correções publicadas sejam refletidas de imediato; o cache atende apenas na ausência de conectividade. |
| Demais recursos | Cache com recurso à rede | Ícones e fontes são imutáveis entre versões; o atendimento local reduz a latência. |

A versão do cache é declarada na constante `CACHE`. A alteração desse valor
invalida o conteúdo anterior durante a ativação.

### Fluxo de instalação

O comportamento diverge entre plataformas e é tratado em ramos distintos.

| Plataforma | Mecanismo | Implementação |
| --- | --- | --- |
| Chrome e derivados | Evento `beforeinstallprompt` | O evento é interceptado e armazenado; a interface aciona `prompt()` sob interação do usuário. |
| Safari em iOS | Inexistente | A interface apresenta as instruções do menu Compartilhar, única via disponível na plataforma. |
| Convite indisponível | — | A interface apresenta o caminho manual pelo menu do navegador. |

O ouvinte de `beforeinstallprompt` é registrado em bloco dedicado no `<head>`.
O motivo consta em [Decisões técnicas](#decisões-técnicas).

---

## Decisões técnicas

| Decisão | Alternativa considerada | Justificativa |
| --- | --- | --- |
| Arquivo único, sem etapa de compilação | Empacotador com módulos separados | O ciclo de vida do artefato é curto e as correções tendem a ocorrer às vésperas da viagem. A ausência de dependências dispensa ambiente configurado para editar um horário. |
| Conteúdo em HTML | Renderização a partir de estrutura de dados | A renderização em JavaScript tornaria o conteúdo indisponível sem script e comprometeria a impressão. Em um documento cuja função é informar, o conteúdo deve residir no documento. |
| Rede prioritária para navegação | Cache prioritário uniforme | Um roteiro retido em versão desatualizada representa risco superior ao de meio segundo adicional de carregamento. |
| Ícone iOS embutido em base64 | Referência a arquivo externo | O Safari não interpreta SVG em `apple-touch-icon`, e caminhos relativos falham quando a página é servida fora da raiz. O custo é de aproximadamente 8 KB. |
| `beforeinstallprompt` registrado no `<head>` | Registro junto ao restante do script | Em visitas subsequentes, com o *service worker* já ativo, o evento é disparado antes do processamento do final do documento. O registro tardio resulta em perda do evento. |
| Estados de `:hover` sob `@media (hover: hover)` | Declaração incondicional | Em dispositivos sensíveis ao toque, o estado permanece aplicado ao último elemento tocado. |
| Contraste verificado por medição | Seleção visual de cores | A versão inicial apresentava separadores de tabela em 1,3:1, insuficientes para delimitar as linhas. |

---

## Acessibilidade

- Marcação semântica: `header`, `nav`, `main`, `section` e listas ordenadas para
  sequências temporais.
- `aria-current` no item de navegação correspondente à seção visível,
  `aria-label` na navegação e `aria-hidden` em elementos decorativos.
- Contraste medido em todos os pares de texto e fundo:

  | Elemento | Razão de contraste | Critério WCAG 2.1 |
  | --- | --- | --- |
  | Texto principal | 14,05:1 | AAA |
  | Texto secundário | 6,06:1 | AAA |
  | Rótulos reduzidos | 8,36:1 | AAA |
  | Separadores de tabela | 2,52:1 | Elemento não textual |

- Alvos de toque com altura mínima de 40 pixels.
- `prefers-reduced-motion` suprime a animação da trilha, as transições de
  entrada e a rolagem suave.
- `scroll-margin-top` nas seções, para compensar a barra de navegação fixa.
- Indicação de foco por `:focus-visible`.
- O conteúdo é integralmente acessível sem JavaScript. Dependem de script apenas
  o indicador de estado da viagem, o destaque da seção corrente e a oferta de
  instalação.

---

## Compatibilidade

| Recurso | Chrome / Android | Safari / iOS | Navegadores de desktop |
| --- | --- | --- | --- |
| Conteúdo, impressão e vínculos | Suportado | Suportado | Suportado |
| Instalação na tela de início | Convite nativo | Menu Compartilhar | Chrome e Edge |
| Operação sem conexão | Suportado | Suportado | Suportado |
| Execução sem interface do navegador | Suportado | Suportado | Suportado |

As propriedades `backdrop-filter` e `mask-image` degradam sem comprometer o
layout em navegadores que não as implementam.

---

## Estrutura de diretórios

```
.
├── index.html              documento único: conteúdo, estilos e comportamento
├── manifest.webmanifest    metadados da aplicação instalável
├── sw.js                   service worker
├── favicon.svg             ícone do navegador
├── icon-192.png            ícone da aplicação (Android)
├── icon-512.png            ícone em alta resolução e tela de abertura
├── apple-touch-icon.png    ícone da aplicação (iOS)
├── robots.txt              diretrizes para rastreadores
├── _headers                cabeçalhos HTTP (Netlify)
├── _redirects              regras de reescrita (Netlify)
├── docs/
│   └── preview.png         imagem de apresentação
└── tools/
    └── make-icons.py       geração dos ícones a partir do vetor
```

---

## Contribuição

Correções e sugestões são bem-vindas por meio de *issues* e *pull requests*.
Solicita-se observar:

- Preservação da ausência de dependências de execução.
- Manutenção das razões de contraste documentadas na seção de acessibilidade.
- Verificação do comportamento em navegador móvel antes da submissão, em
  especial quanto a estados de toque e à área de rolagem horizontal da barra de
  navegação.
- Conformidade com o `.editorconfig` do repositório.

---

## Licença

Distribuído sob a licença MIT. O texto integral consta em [LICENSE](LICENSE).

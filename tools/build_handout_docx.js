const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, PageBreak,
  HeadingLevel, VerticalAlign,
} = require("docx");

const FONT  = "Meiryo";
const NAVY  = "1A5276";
const GREEN = "1D9E75";
const DARK  = "1C2833";
const GRAY  = "566573";
const LITE  = "F4F8FA";
const GRNLT = "EAF7F1";
const W     = 10466;              // 本文の幅（DXA）

const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none };
const thin = (color) => ({ style: BorderStyle.SINGLE, size: 4, color });

function P(text, o = {}) {
  return new Paragraph({
    alignment: o.align,
    spacing: { before: o.before || 0, after: o.after === undefined ? 40 : o.after, line: o.line || 240 },
    border: o.border,
    indent: o.indent,
    children: (Array.isArray(text) ? text : [text]).map((t) =>
      typeof t === "string"
        ? new TextRun({ text: t, font: FONT, size: o.size || 18, bold: o.bold, color: o.color || DARK })
        : new TextRun({ font: FONT, size: o.size || 18, color: o.color || DARK, ...t })),
  });
}

function head(num, title) {
  return new Paragraph({
    spacing: { before: 200, after: 90 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: GREEN, space: 3 } },
    children: [
      new TextRun({ text: num + "  ", font: FONT, size: 20, bold: true, color: GREEN }),
      new TextRun({ text: title, font: FONT, size: 22, bold: true, color: NAVY }),
    ],
  });
}

function cell(children, o = {}) {
  return new TableCell({
    width: { size: o.w, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    verticalAlign: VerticalAlign.CENTER,
    columnSpan: o.span,
    children: Array.isArray(children) ? children : [children],
  });
}

function table(rows, widths) {
  return new Table({
    columnWidths: widths,
    width: { size: W, type: WidthType.DXA },
    borders: {
      top: thin("D5DDE3"), bottom: thin("D5DDE3"),
      left: thin("D5DDE3"), right: thin("D5DDE3"),
      insideHorizontal: thin("D5DDE3"), insideVertical: thin("D5DDE3"),
    },
    rows,
  });
}

/* ---------- 1枚目 ---------- */
const page1 = [];

page1.push(P("介護保険サービス ／ 地域在宅医療連携のご案内", { size: 15, color: GRAY, after: 30 }));
page1.push(P("訪問入浴介護　サービス案内", { size: 40, bold: true, color: NAVY, after: 40 }));
page1.push(P("在宅で入浴が困難な方へ、専門チームがお伺いします。",
  { size: 18, color: GRAY, after: 60,
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 6 } } }));

page1.push(head("01", "訪問入浴介護とは"));
page1.push(P("看護師1名＋介護スタッフ2名の3名チーム（厚生労働省令で定められた体制）が、専用の組立式浴槽を車両で持参してご自宅を訪問し、居室で全身浴を提供する介護保険サービスです。ベッドサイドに約2畳のスペースがあれば、浴室の広さや段差にかかわらず実施できます。入浴前後は看護師が入浴可否を判断し、異常があれば清拭・部分浴へ切り替えて関係職種へ報告します。"));

page1.push(head("02", "こんな方にご利用いただけます"));
const targets = [
  ["寝たきり・重度要介護の方", "自宅の浴室での入浴が困難な方"],
  ["デイサービスへの通所が難しい方", "外出が体調的に困難な方"],
  ["一人暮らしで介助者がいない方", "ご家族だけでの入浴介助に限界がある方"],
];
page1.push(table(
  targets.map((r) => new TableRow({
    children: r.map((t) => cell(P([{ text: "●　", color: GREEN, bold: true }, { text: t }], { after: 0 }),
      { w: W / 2, fill: LITE })),
  })), [W / 2, W / 2]));
page1.push(P("※気管切開・経管栄養・在宅酸素等の方も、主治医の許可があれば対応できる場合が多くあります。利用者は要介護5が48.2%・要介護4が25.1%と、約4分の3が重度の方です（日本在宅介護協会 2025年調査）。",
  { size: 15, color: GRAY, before: 80 }));

page1.push(head("03", "入浴支援サービスの比較"));
const cw = [2666, 1560, 1560, 1560, 1560, 1560];
const cmpHead = ["項目", "訪問入浴", "訪問看護", "訪問介護", "デイ入浴", "清拭・部分浴"];
const cmpRows = [
  ["自宅で受けられる", "✓", "✓", "✓", "✕", "✓"],
  ["全身浴ができる", "✓", "△", "△", "✓", "✕"],
  ["浴室の環境に左右されない", "✓", "✕", "✕", "✓", "✓"],
  ["看護師が同行", "✓", "✓", "✕", "△", "△"],
  ["複数名での移乗介助", "✓", "△", "△", "✓", "△"],
  ["重度・寝たきり対応", "✓", "△", "△", "△", "△"],
  ["バイタル・皮膚観察", "✓", "✓", "✕", "△", "✕"],
  ["在宅チームへ情報共有", "✓", "✓", "✓", "✓", "✓"],
];
const rows = [new TableRow({
  tableHeader: true,
  children: cmpHead.map((t, i) => cell(
    P(t, { size: 16, bold: true, color: "FFFFFF", align: i ? AlignmentType.CENTER : undefined, after: 0 }),
    { w: cw[i], fill: i === 1 ? GREEN : NAVY })),
})];
for (const r of cmpRows) {
  rows.push(new TableRow({
    children: r.map((t, i) => cell(
      P(t, { size: 16, bold: i === 1, color: i === 1 ? GREEN : DARK,
             align: i ? AlignmentType.CENTER : undefined, after: 0 }),
      { w: cw[i], fill: i === 1 ? GRNLT : undefined })),
  }));
}
page1.push(table(rows, cw));
page1.push(P("✓ 対応できる　　△ 事業所・状態により異なる　　✕ 対応が難しい　　※「訪問看護」「訪問介護」欄は自宅の浴室での入浴介助を指します。清拭・部分浴はサービス種別を問わず実施される方法です。",
  { size: 14, color: GRAY, before: 60 }));
page1.push(P("「自宅で・全身浴を・看護師付きで・重度でも」── この4条件を同時に満たせるのは訪問入浴介護だけです。",
  { size: 18, bold: true, color: GREEN }));

page1.push(head("04", "サービスの流れ（サービス提供時間 45分以内）"));
const flow = [
  ["15分", "準備・設置", "到着・体調確認／浴槽の搬入・組立\nバイタル確認・入浴可否の判断"],
  ["15分", "入　浴", "全身浴・洗髪\n入浴中の全身観察"],
  ["15分", "片付け・記録", "更衣・保湿ケア／機材の撤収\n記録と関係職種への連絡"],
];
page1.push(table([new TableRow({
  children: flow.map(([m, t, d]) => cell([
    P(m, { size: 20, bold: true, color: GREEN, align: AlignmentType.CENTER, after: 20 }),
    P(t, { size: 18, bold: true, color: NAVY, align: AlignmentType.CENTER, after: 30 }),
    ...d.split("\n").map((line) => P(line, { size: 14, color: GRAY, align: AlignmentType.CENTER, after: 0 })),
  ], { w: Math.floor(W / 3), fill: LITE })),
})], [Math.floor(W / 3), Math.floor(W / 3), W - 2 * Math.floor(W / 3)]));
page1.push(P("※床・寝具の養生と原状復帰までスタッフが対応し、ご家族が介助に入る必要はありません。",
  { size: 15, color: GRAY, before: 60 }));

page1.push(head("05", "看護師の視点と、訪問看護との役割分担"));
page1.push(P("訪問入浴は介護保険サービスのため医療行為は行えません。異常を見つけて訪問看護・主治医へつなぐのが役割です。",
  { size: 16, color: GRAY }));
const roleL = ["バイタル測定と入浴可否の判断", "入浴時の全身観察（褥瘡・浮腫・皮膚）",
               "洗身・洗髪と日常的な保湿ケア", "観察所見の記録と当日中の報告"];
const roleR = ["褥瘡・創傷の処置、薬剤の塗布", "点滴・注射・採血、カテーテル管理",
               "喀痰吸引・経管栄養の管理", "医師の指示に基づく医療的ケア全般"];
const half = Math.floor(W / 2);
page1.push(table([new TableRow({
  children: [
    cell([P("訪問入浴が担うこと", { size: 18, bold: true, color: GREEN, after: 40 }),
          ...roleL.map((t) => P([{ text: "・" }, { text: t }], { size: 16, after: 0 }))],
      { w: half, fill: GRNLT }),
    cell([P("訪問看護におつなぎすること", { size: 18, bold: true, color: NAVY, after: 40 }),
          ...roleR.map((t) => P([{ text: "・" }, { text: t }], { size: 16, after: 0 }))],
      { w: W - half, fill: LITE }),
  ],
})], [half, W - half]));

/* ---------- 2枚目 ---------- */
const page2 = [];
page2.push(new Paragraph({ children: [new PageBreak()] }));
page2.push(P("訪問入浴介護　サービス案内 ／ 裏面", { size: 15, color: GRAY, after: 30 }));
page2.push(P("ご依頼にあたって", { size: 32, bold: true, color: NAVY, after: 40 }));
page2.push(P("介護報酬・看護連携・よくあるご質問",
  { size: 18, color: GRAY, after: 60,
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 6 } } }));

page2.push(head("06", "介護報酬・単位数"));
const fw = [7466, 3000];
const feeRows = [
  ["h", "サービス", "単位数"],
  ["m", "訪問入浴介護費（1回）　看護師1名＋介護スタッフ2名の3名体制（省令上の要件）・専用浴槽持参・全身浴", "1,266 単位／回"],
  ["m", "清拭・部分浴（1回）", "1,139 単位／回"],
  ["h", "主な加算", "単位数"],
  ["", "初回加算（月1回）", "200 単位"],
  ["", "看取り連携体制加算（2024年新設）", "64 単位"],
  ["", "認知症専門ケア加算（Ⅰ）", "3 単位／日"],
  ["", "認知症専門ケア加算（Ⅱ）", "4 単位／日"],
  ["", "介護職員等処遇改善加算　加算Ⅱ（ロ）", "12.7 ％"],
].map(([kind, a, b]) => new TableRow({
  children: [
    cell(P(a, { size: kind === "h" ? 16 : 17, bold: kind !== "", color: kind === "h" ? "FFFFFF" : DARK, after: 0 }),
      { w: fw[0], fill: kind === "h" ? NAVY : (kind === "m" ? GRNLT : undefined) }),
    cell(P(b, { size: kind === "h" ? 16 : 18, bold: true, color: kind === "h" ? "FFFFFF" : GREEN,
               align: AlignmentType.RIGHT, after: 0 }),
      { w: fw[1], fill: kind === "h" ? NAVY : (kind === "m" ? GRNLT : undefined) }),
  ],
}));
page2.push(table(feeRows, fw));
page2.push(P("※2024年4月介護報酬改定後の単位数。1単位あたりの単価は地域区分により異なります。",
  { size: 14, color: GRAY, before: 60 }));

page2.push(head("07", "訪問看護のみなさまへ ── 連携のお願い"));
const asks = [
  ["① 訪問日を合わせてください", "入浴直後は皮膚が清潔で、創部の処置に最も適した状態です。"],
  ["② 見てほしい部位をお知らせください", "重点的に観察し、当日中に連絡ノート・電話・写真でお返しします。"],
  ["③ 医療的ケアのある方は事前にご相談を", "主治医の指示内容を共有いただければ、受け入れ可否を一緒に検討します。"],
];
for (const [t, d] of asks) {
  page2.push(P(t, { size: 18, bold: true, color: NAVY, before: 80, after: 20 }));
  page2.push(P(d, { size: 16, color: GRAY }));
}

page2.push(head("08", "よくあるご質問"));
const qa = [
  ["どんな状態の方が利用できますか？", "要介護1〜5の認定を受けた方が対象です。寝たきりの方、気管切開・経管栄養中の方でも、主治医の許可があれば対応できるケースが多くあります。"],
  ["費用はどのくらいかかりますか？", "介護保険適用で、1割負担の方は1回あたり約1,000〜1,300円が目安です。"],
  ["緊急時の対応はどうなりますか？", "看護師が同行しているため、その場で状態を判断します。必要時は主治医・訪問看護師・119番へ連絡します。"],
  ["医療処置もお願いできますか？", "訪問入浴は介護保険サービスのため医療行為は行えません。処置が必要な場合は訪問看護と連携し、入浴日に合わせてご訪問いただく形をおすすめしています。"],
  ["ケアマネジャーとして、どう依頼すればいいですか？", "ケアプランに位置づけ後、お電話またはFAXでご連絡ください。初回アセスメントは無料で伺います。"],
];
for (const [q, a] of qa) {
  page2.push(P([{ text: "Q　", bold: true, color: GREEN }, { text: q, bold: true }],
    { size: 17, before: 70, after: 10 }));
  page2.push(P([{ text: "A　", bold: true, color: NAVY }, { text: a }], { size: 16, color: GRAY }));
}

page2.push(table([new TableRow({
  children: [cell([
    P("アップルハート八幡西訪問入浴センター", { size: 22, bold: true, color: "FFFFFF", after: 50 }),
    P("TEL 093-695-7766　　FAX 093-695-7767", { size: 20, bold: true, color: "FFFFFF", after: 30 }),
    P("担当　冨永　一心（管理者・看護師）", { size: 16, color: "FFFFFF", after: 30 }),
    P("まずはご相談から。お気軽にどうぞ。初回アセスメントは無料でお伺いします。",
      { size: 16, color: "FFFFFF", after: 0 }),
  ], { w: W, fill: NAVY })],
})], [W]));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 18, color: DARK } } } },
  sections: [{
    properties: { page: { margin: { top: 720, right: 720, bottom: 600, left: 720 } } },
    children: [...page1, ...page2],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync("/home/user/houmonnyuyoku/配布資料.docx", b);
  console.log("書き出しました:", b.length, "バイト");
});

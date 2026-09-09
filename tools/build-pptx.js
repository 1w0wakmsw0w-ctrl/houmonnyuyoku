const pptxgen = require('pptxgenjs');

const P='1A5276', S='1D9E75', A='2E86C1', TX='1C2833', SUB='566573',
      GY='BDC3C7', AM='F39C12', TINT='F4F8FA', TG='EAF7F1', WH='FFFFFF', MINT='7EE2BC';
const F='Meiryo';
const W=13.333, H=7.5, M=0.62, CW=W-2*M;

const pres=new pptxgen();
pres.layout='LAYOUT_WIDE';
pres.author='アップルハート八幡西訪問入浴センター';
pres.title='自宅でお風呂に入る権利 — 訪問入浴介護の役割と可能性';

// "**bold**" -> runs; bold parts take the accent colour
function runs(str, o={}){
  const base={fontFace:F, fontSize:o.fontSize||13, color:o.color||TX, ...o};
  const out=[];
  str.split(/(\*\*[^*]+\*\*)/).filter(Boolean).forEach(p=>{
    if(p.startsWith('**')) out.push({text:p.slice(2,-2), options:{...base, bold:true, color:o.strong||S}});
    else out.push({text:p, options:{...base}});
  });
  return out;
}
// bulleted list from ["**題**　説明", ...]
function bullets(items, o={}){
  const arr=[];
  items.forEach((it,i)=>{
    const r=runs(it,o);
    r[0].options={...r[0].options, bullet:{code:'25CF'}};
    r[r.length-1].options={...r[r.length-1].options, breakLine:i<items.length-1};
    arr.push(...r);
  });
  return arr;
}
function header(slide, chap, name, title){
  if(chap){
    slide.addShape(pres.ShapeType.roundRect,{x:M,y:0.36,w:1.62,h:0.34,fill:{color:P},rectRadius:0.05,line:{color:P}});
    slide.addText(chap,{x:M,y:0.36,w:1.62,h:0.34,fontFace:F,fontSize:11,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
    slide.addText(name,{x:M+1.78,y:0.36,w:6,h:0.34,fontFace:F,fontSize:12,color:SUB,valign:'middle',isTextBox:true,margin:0});
  }
  slide.addText(title,{x:M,y:0.82,w:CW,h:0.62,fontFace:F,fontSize:30,bold:true,color:P,valign:'middle',isTextBox:true,margin:0});
}
function card(slide,{x,y,w,h,fill,title,titleColor,items,body,fontSize}){
  slide.addShape(pres.ShapeType.roundRect,{x,y,w,h,fill:{color:fill||TINT},rectRadius:0.06,line:{color:fill||TINT}});
  let cy=y+0.2;
  if(title){
    slide.addText(title,{x:x+0.24,y:cy,w:w-0.48,h:0.34,fontFace:F,fontSize:15,bold:true,color:titleColor||P,valign:'middle',isTextBox:true,margin:0});
    cy+=0.44;
  }
  if(items) slide.addText(bullets(items,{fontSize:fontSize||12.5}),
    {x:x+0.24,y:cy,w:w-0.48,h:y+h-cy-0.16,paraSpaceAfter:6,valign:'top',isTextBox:true,margin:0});
  if(body) slide.addText(runs(body,{fontSize:fontSize||12.5}),
    {x:x+0.24,y:cy,w:w-0.48,h:y+h-cy-0.16,lineSpacingMultiple:1.25,valign:'top',isTextBox:true,margin:0});
}
function banner(slide,{x,y,w,h,fill,text,size,color}){
  slide.addShape(pres.ShapeType.roundRect,{x,y,w,h,fill:{color},rectRadius:0.07,line:{color}});
  slide.addText(text,{x:x+0.2,y,w:w-0.4,h,fontFace:F,fontSize:size||16,bold:true,color:fill,align:'center',valign:'middle',isTextBox:true,margin:0});
}
function contactBlock(slide,y,dark){
  const lab=dark?MINT:SUB, val=dark?WH:TX;
  slide.addText('アップルハート八幡西訪問入浴センター',{x:M,y,w:8.2,h:0.5,fontFace:F,fontSize:23,bold:true,color:dark?WH:P,valign:'middle',isTextBox:true,margin:0});
  const rows=[['担当','冨永　一心（管理者・看護師）',15],['TEL','093-695-7766',24],['FAX','093-695-7767',15]];
  let ry=y+0.66;
  rows.forEach(([k,v,sz])=>{
    slide.addText(k,{x:M,y:ry,w:0.9,h:0.44,fontFace:F,fontSize:12,bold:true,color:lab,valign:'middle',isTextBox:true,margin:0});
    slide.addText(v,{x:M+1.0,y:ry,w:6.6,h:0.44,fontFace:F,fontSize:sz,bold:true,color:k==='TEL'?(dark?MINT:S):val,valign:'middle',isTextBox:true,margin:0});
    ry+=0.52;
  });
  slide.addShape(pres.ShapeType.roundRect,{x:W-M-2.3,y:y+0.05,w:2.3,h:2.3,fill:{color:dark?P:WH},rectRadius:0.06,line:{color:GY,width:1.5,dashType:'dash'}});
  slide.addText('QRコード\n（お問い合わせ用）',{x:W-M-2.3,y:y+0.05,w:2.3,h:2.3,fontFace:F,fontSize:11,color:dark?GY:SUB,align:'center',valign:'middle',isTextBox:true,margin:0});
}

/* ---------- 1. 表紙 ---------- */
let s=pres.addSlide();
s.background={color:P};
s.addText('地域在宅医療情報交換会',{x:M,y:1.15,w:CW,h:0.36,fontFace:F,fontSize:14,bold:true,color:MINT,charSpacing:2,isTextBox:true,margin:0});
s.addText('自宅でお風呂に入る権利',{x:M,y:1.66,w:CW,h:1.5,fontFace:F,fontSize:52,bold:true,color:WH,valign:'middle',isTextBox:true,margin:0});
s.addText('訪問入浴介護の役割と可能性',{x:M,y:3.3,w:CW,h:0.5,fontFace:F,fontSize:22,color:MINT,valign:'middle',isTextBox:true,margin:0});
s.addShape(pres.ShapeType.rect,{x:M,y:4.32,w:CW,h:0.02,fill:{color:'3D6E8C'},line:{color:'3D6E8C'}});
s.addText([{text:'アップルハート八幡西訪問入浴センター',options:{fontFace:F,fontSize:17,bold:true,color:WH,breakLine:true}},
  {text:'管理者・看護師　冨永　一心',options:{fontFace:F,fontSize:14,color:'C9DCE8',breakLine:true}},
  {text:'2026年10月15日（木）19:00〜',options:{fontFace:F,fontSize:14,color:'C9DCE8'}}],
  {x:M,y:4.6,w:CW,h:1.4,lineSpacingMultiple:1.4,isTextBox:true,margin:0});
s.addNotes('本日は訪問入浴介護についてお話しします。テーマは「自宅でお風呂に入る権利」。在宅で入浴が困難な方に、どう関わり、どう連携できるかをお伝えします。');

/* ---------- 2. Ch1-1 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 1','課題提起','「在宅で入浴できない」という現実');
card(s,{x:M,y:1.66,w:CW/2-0.16,h:3.35,fill:TINT,title:'入浴を阻む壁',items:[
 '浴槽をまたげない・立位が保てない','浴室が狭く介助スペースがない',
 'ご家族だけでは支えきれない（転倒・腰痛）','医療的ケアがあり不安で踏み切れない','通所への外出そのものが負担']});
card(s,{x:M+CW/2+0.16,y:1.66,w:CW/2-0.16,h:3.35,fill:TG,title:'入浴がもつ意義',titleColor:S,items:[
 '**清潔保持**　全身の洗浄・洗髪','**感染予防**　尿路・呼吸器感染リスクの低減',
 '**皮膚トラブル予防**　褥瘡・浸軟の抑制','**QOL**　温熱による安楽・睡眠の改善','**生きる意欲**　「人として当たり前」の回復']});
s.addText(runs('結果として「週1回の清拭のみ」「数か月入浴なし」という状態が生まれます。入浴は**贅沢ではなく、在宅療養を支える医療的・生活的インフラ**です。',{fontSize:15}),
  {x:M,y:5.28,w:CW,h:0.9,lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addNotes('入浴困難は「できない理由」が複数重なって起こります。清拭だけでは代替できない意義があることを押さえてください。');

/* ---------- 3. Ch1-2 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 1','課題提起','入浴支援の選択肢と、その限界');
const w3=(CW-0.44)/3;
card(s,{x:M,y:1.66,w:w3,h:3.1,fill:TINT,title:'① 訪問介護・訪問看護',body:'自宅の浴室を使い、ヘルパーや看護師が介助。清拭・部分浴も含む。\n\n**限界：**浴室環境に左右され原則1名対応。全介助や寝たきりの方は難しい。',fontSize:12.5});
card(s,{x:M+w3+0.22,y:1.66,w:w3,h:3.1,fill:TINT,title:'② デイサービス入浴',body:'週複数回、社会参加とあわせて実施できる。\n\n**限界：**通所という外出が前提。寝たきり・全介助・医療的ケアがあると受け入れ困難。',fontSize:12.5});
card(s,{x:M+2*(w3+0.22),y:1.66,w:w3,h:3.1,fill:TG,title:'③ 訪問入浴介護',titleColor:S,body:'専用浴槽を持ち込み、自宅で全身浴を提供。\n\n**特徴：**看護師同行で重度でも対応可。移動の負担がゼロ。',fontSize:12.5});
s.addShape(pres.ShapeType.roundRect,{x:M,y:5.02,w:CW,h:0.92,fill:{color:'FDF3E3'},rectRadius:0.06,line:{color:'FDF3E3'}});
s.addText([{text:'空白地帯：',options:{fontFace:F,fontSize:15,bold:true,color:'B9770E'}},
  {text:'「デイには行けない、でも清拭では足りない」——重度化した在宅療養者ほど、この谷間に落ちます。',options:{fontFace:F,fontSize:15,color:TX}}],
  {x:M+0.28,y:5.02,w:CW-0.56,h:0.92,valign:'middle',isTextBox:true,margin:0});
s.addNotes('3つの選択肢それぞれに限界があること、そしてその間に空白地帯があることが今日の出発点です。');

/* ---------- 4. Ch2-1 比較表 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 2','比較・差別化','5つの入浴支援を比べる');
const mk=(c,col)=>({text:c,options:{fontFace:F,fontSize:15,bold:true,color:col,align:'center',valign:'middle'}});
const OK=()=>mk('\u2713',S), NO=()=>mk('\u2715',GY), TR=()=>mk('\u25B3',AM);
const hdr=t=>({text:t,options:{fontFace:F,fontSize:11,bold:true,color:WH,align:'center',valign:'middle',fill:{color:P}}});
const hdrOwn=t=>({text:t,options:{fontFace:F,fontSize:11,bold:true,color:WH,align:'center',valign:'middle',fill:{color:S}}});
const lbl=t=>({text:t,options:{fontFace:F,fontSize:11.5,bold:true,color:TX,align:'left',valign:'middle',fill:{color:TINT}}});
const own=m=>({...m,options:{...m.options,fill:{color:TG}}});
const rowsData=[
 ['自宅で受けられる',        OK,OK ,OK ,NO ,OK ],
 ['全身浴ができる',          OK,TR ,TR ,OK ,NO ],
 ['浴室の環境に左右されない',OK,NO ,NO ,OK ,OK ],
 ['看護師が同行',            OK,OK ,NO ,TR ,NO ],
 ['複数名での移乗介助',      OK,NO ,NO ,OK ,NO ],
 ['重度・寝たきり対応',      OK,TR ,NO ,NO ,TR ],
 ['バイタル・皮膚観察',      OK,OK ,NO ,TR ,NO ],
 ['在宅チームへ情報共有',    OK,OK ,TR ,NO ,NO ]];
const tbl=[[hdr('項目'),hdrOwn('訪問入浴'),hdr('訪問看護'),hdr('訪問介護'),hdr('デイ入浴'),hdr('清拭・部分浴')]];
rowsData.forEach(r=>tbl.push([lbl(r[0]),own(r[1]()),r[2](),r[3](),r[4](),r[5]()]));
s.addTable(tbl,{x:M,y:1.58,w:CW,colW:[3.3,1.82,1.75,1.75,1.75,1.71],rowH:0.36,
  border:{type:'solid',color:'E5E9EC',pt:1},fontFace:F,valign:'middle'});
s.addText([{text:'\u2713 対応できる',options:{fontFace:F,fontSize:10.5,color:S}},
  {text:'\u3000\u3000\u25B3 事業所・状態により異なる',options:{fontFace:F,fontSize:10.5,color:AM}},
  {text:'\u3000\u3000\u2715 対応が難しい',options:{fontFace:F,fontSize:10.5,color:SUB,breakLine:true}},
  {text:'\u203B「訪問看護」「訪問介護」欄は自宅の浴室での入浴介助を指します。清拭・部分浴はサービス種別を問わず実施される方法です。',
   options:{fontFace:F,fontSize:10,color:SUB}}],
  {x:M,y:4.72,w:CW,h:0.62,lineSpacingMultiple:1.4,isTextBox:true,margin:0});
s.addShape(pres.ShapeType.roundRect,{x:M,y:5.42,w:CW,h:0.66,fill:{color:TG},rectRadius:0.05,line:{color:TG}});
s.addText([{text:'訪問入浴の利用者は',options:{fontFace:F,fontSize:14,color:TX}},
  {text:'要介護5が48.2%、要介護4が25.1%',options:{fontFace:F,fontSize:14,bold:true,color:S}},
  {text:'——約4分の3が要介護4〜5の重度の方です。',options:{fontFace:F,fontSize:14,bold:true,color:TX}},
  {text:'（日本在宅介護協会 2025年調査）',options:{fontFace:F,fontSize:11,color:SUB}}],
  {x:M+0.28,y:5.42,w:CW-0.56,h:0.66,valign:'middle',isTextBox:true,margin:0});
s.addNotes('この表が本日の中心です。訪問看護・訪問介護の入浴介助も比較に入れました。訪問入浴の違いは、専用浴槽を持参するため浴室環境に左右されない点と、3名体制で移乗できる点です。');

/* ---------- 5. Ch2-2 4条件 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 2','比較・差別化','訪問入浴にしかできないこと');
const four=[['1','自宅で','移動・外出の負担なし'],['2','全身浴を','洗髪・背部まで温める'],
            ['3','看護師付きで','毎回のアセスメント'],['4','重度でも','寝たきり・全介助でも']];
const w4=(CW-0.66)/4;
four.forEach((f,i)=>{
  const x=M+i*(w4+0.22);
  s.addShape(pres.ShapeType.roundRect,{x,y:1.7,w:w4,h:1.85,fill:{color:TG},rectRadius:0.07,line:{color:S,width:1.25}});
  s.addShape(pres.ShapeType.ellipse,{x:x+w4/2-0.28,y:1.94,w:0.56,h:0.56,fill:{color:S},line:{color:S}});
  s.addText(f[0],{x:x+w4/2-0.28,y:1.94,w:0.56,h:0.56,fontFace:F,fontSize:19,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
  s.addText(f[1],{x:x+0.1,y:2.62,w:w4-0.2,h:0.36,fontFace:F,fontSize:17,bold:true,color:P,align:'center',valign:'middle',isTextBox:true,margin:0});
  s.addText(f[2],{x:x+0.06,y:2.96,w:w4-0.12,h:0.52,fontFace:F,fontSize:11,color:SUB,align:'center',valign:'top',isTextBox:true,margin:0});
});
s.addShape(pres.ShapeType.roundRect,{x:M,y:3.82,w:CW,h:1.28,fill:{color:P},rectRadius:0.07,line:{color:P}});
s.addText([{text:'この',options:{fontFace:F,fontSize:22,bold:true,color:WH}},
  {text:'4つの条件',options:{fontFace:F,fontSize:22,bold:true,color:MINT}},
  {text:'を同時に満たせるのは、在宅サービスの中で',options:{fontFace:F,fontSize:22,bold:true,color:WH}},
  {text:'訪問入浴介護だけ',options:{fontFace:F,fontSize:22,bold:true,color:MINT}},
  {text:'です。',options:{fontFace:F,fontSize:22,bold:true,color:WH}}],
  {x:M+0.35,y:3.82,w:CW-0.7,h:1.28,align:'center',valign:'middle',lineSpacingMultiple:1.25,isTextBox:true,margin:0});
s.addText('どれか1つなら他のサービスでも代替できます。しかし「重度化しても、自宅のまま、湯船に浸かり続ける」ことを保証できるのは訪問入浴だけ——ここが在宅療養の継続を左右します。',
  {x:M,y:5.28,w:CW,h:0.8,fontFace:F,fontSize:13,color:SUB,lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addNotes('4条件のうち3つまでなら他サービスでも満たせます。4つ同時、という点が訪問入浴の存在理由です。');

/* ---------- 6. Ch3-1 流れ ---------- */
s=pres.addSlide();
header(s,'CHAPTER 3','サービスの実際','訪問の流れ（サービス提供時間 45分以内）');
const phases=[['準備・設置','到着・ご挨拶／当日の体調確認\n専用浴槽の搬入・組立\nバイタル確認と入浴可否の判断',0],
 ['入　浴','全身浴・洗髪\n入浴中の全身観察\n（褥瘡・浮腫・皮膚の状態）',1],
 ['片付け・記録','更衣・保湿ケア／整容\n機材の撤収・原状復帰\n記録と関係職種への連絡',0]];
const wp=(CW-2*0.34)/3;
phases.forEach((ph,i)=>{
  const x=M+i*(wp+0.34);
  s.addShape(pres.ShapeType.roundRect,{x,y:1.7,w:wp,h:2.5,fill:{color:ph[2]?TG:TINT},rectRadius:0.07,line:{color:ph[2]?TG:TINT}});
  s.addShape(pres.ShapeType.roundRect,{x:x+wp/2-0.52,y:1.94,w:1.04,h:0.36,fill:{color:ph[2]?S:P},rectRadius:0.05,line:{color:ph[2]?S:P}});
  s.addText('15分',{x:x+wp/2-0.52,y:1.94,w:1.04,h:0.36,fontFace:F,fontSize:13,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
  s.addText(ph[0],{x:x+0.12,y:2.42,w:wp-0.24,h:0.4,fontFace:F,fontSize:20,bold:true,color:P,align:'center',valign:'middle',isTextBox:true,margin:0});
  s.addText(ph[1],{x:x+0.12,y:2.88,w:wp-0.24,h:1.2,fontFace:F,fontSize:12.5,color:SUB,align:'center',valign:'top',lineSpacingMultiple:1.35,isTextBox:true,margin:0});
  if(i<2) s.addText('›',{x:x+wp,y:1.7,w:0.34,h:2.5,fontFace:F,fontSize:26,bold:true,color:GY,align:'center',valign:'middle',isTextBox:true,margin:0});
});
card(s,{x:M,y:4.44,w:CW/2-0.16,h:1.62,fill:TINT,title:'入浴できないと判断した場合',
  body:'発熱・血圧変動・全身状態の悪化時は、看護師の判断で**清拭や部分浴に切り替え**。中止時もご家族・ケアマネジャーへ理由を報告します。',fontSize:12.5});
card(s,{x:M+CW/2+0.16,y:4.44,w:CW/2-0.16,h:1.62,fill:TG,title:'住環境への配慮',titleColor:S,
  body:'給湯は**車両または屋内の給湯設備**から。ベッドサイドに約2畳のスペースがあれば設置可能。床・寝具の養生も行います。',fontSize:12.5});
s.addNotes('準備・入浴・片付けの3区分、各15分で計45分以内です。入浴可否の判断と記録・連絡が看護師の関わる部分になります。');

/* ---------- 7. Ch3-2 体制 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 3','サービスの実際','スタッフ体制と専門性');
s.addShape(pres.ShapeType.roundRect,{x:M,y:1.66,w:CW*0.53,h:3.05,fill:{color:TG},rectRadius:0.06,line:{color:TG}});
s.addShape(pres.ShapeType.roundRect,{x:M+0.24,y:1.86,w:0.86,h:0.32,fill:{color:S},rectRadius:0.05,line:{color:S}});
s.addText('1名',{x:M+0.24,y:1.86,w:0.86,h:0.32,fontFace:F,fontSize:11,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
s.addText('看護師',{x:M+1.22,y:1.86,w:3,h:0.32,fontFace:F,fontSize:16,bold:true,color:S,valign:'middle',isTextBox:true,margin:0});
s.addText(bullets(['入浴前後の**アセスメント**（バイタル・全身状態）','入浴可否の**その場での判断**',
  '褥瘡・創傷の**観察と記録**（処置は訪問看護へ）','急変時の**初期判断と主治医・訪問看護師への連絡**','関係職種への**情報提供**'],{fontSize:12.5}),
  {x:M+0.24,y:2.34,w:CW*0.53-0.48,h:2.2,paraSpaceAfter:6,valign:'top',isTextBox:true,margin:0});
const x2=M+CW*0.53+0.22, w2=CW*0.47-0.22;
s.addShape(pres.ShapeType.roundRect,{x:x2,y:1.66,w:w2,h:3.05,fill:{color:TINT},rectRadius:0.06,line:{color:TINT}});
s.addShape(pres.ShapeType.roundRect,{x:x2+0.24,y:1.86,w:0.86,h:0.32,fill:{color:A},rectRadius:0.05,line:{color:A}});
s.addText('2名',{x:x2+0.24,y:1.86,w:0.86,h:0.32,fontFace:F,fontSize:11,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
s.addText('介護スタッフ',{x:x2+1.22,y:1.86,w:3,h:0.32,fontFace:F,fontSize:16,bold:true,color:P,valign:'middle',isTextBox:true,margin:0});
s.addText(bullets(['浴槽の搬入・設置・撤去','移乗介助（2名で安全に）','洗身・洗髪、更衣','居室の養生と原状復帰'],{fontSize:12.5}),
  {x:x2+0.24,y:2.34,w:w2-0.48,h:2.2,paraSpaceAfter:6,valign:'top',isTextBox:true,margin:0});
s.addShape(pres.ShapeType.roundRect,{x:M,y:4.98,w:CW,h:1.05,fill:{color:TINT},rectRadius:0.06,line:{color:TINT}});
s.addText([{text:'3名体制は省令上の要件です — ',options:{fontFace:F,fontSize:14,bold:true,color:P}},
  {text:'1回の訪問に看護職員1名＋介護職員2名の計3名と厚生労働省令で定められています。移乗を2名で担うため',options:{fontFace:F,fontSize:14,color:TX}},
  {text:'転倒・皮膚剥離のリスクを抑え',options:{fontFace:F,fontSize:14,bold:true,color:S}},
  {text:'、看護師は',options:{fontFace:F,fontSize:14,color:TX}},
  {text:'観察と判断に専念',options:{fontFace:F,fontSize:14,bold:true,color:S}},
  {text:'できます。',options:{fontFace:F,fontSize:14,color:TX}}],
  {x:M+0.28,y:4.98,w:CW-0.56,h:1.05,valign:'middle',lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addNotes('なぜ3名なのか、という質問をよく受けます。安全確保と、看護師が観察に専念できる体制のためです。');

/* ---------- 8. Ch4-1 全身観察 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 4','看護師の視点・医療連携','入浴は「全身をみる場」です');
s.addText('衣服を脱いだ全身を、明るい場所で、毎回。これは在宅の中で数少ない機会です。',
  {x:M,y:1.6,w:CW,h:0.4,fontFace:F,fontSize:16,color:P,valign:'middle',isTextBox:true,margin:0});
const w3b=(CW-0.44)/3;
card(s,{x:M,y:2.16,w:w3b,h:2.72,fill:TINT,title:'早期発見できるもの',items:[
 '仙骨部・踵部の**褥瘡の発赤**','下腿・足背の**浮腫の増悪**','白癬・湿疹・スキンテア','内出血・打撲痕（転倒の兆候）'],fontSize:12});
card(s,{x:M+w3b+0.22,y:2.16,w:w3b,h:2.72,fill:TINT,title:'体格・栄養の把握',items:[
 '脱衣時の**体型変化・筋肉量の減少**','骨突出の進行（褥瘡リスク上昇）','皮膚の乾燥・ツルゴール低下'],fontSize:12});
card(s,{x:M+2*(w3b+0.22),y:2.16,w:w3b,h:2.72,fill:TG,title:'その日のうちに共有',titleColor:S,items:[
 '主治医へ**創部の状態を報告**','訪問看護師へ**観察所見の申し送り**','ケアマネジャーへ**状態変化の連絡**','必要時は**写真記録**を添えて'],fontSize:12});
s.addShape(pres.ShapeType.roundRect,{x:M,y:5.14,w:CW,h:0.72,fill:{color:TG},rectRadius:0.06,line:{color:TG}});
s.addText('週1〜2回の入浴は、週1〜2回の全身アセスメントでもあります。',
  {x:M+0.28,y:5.14,w:CW-0.56,h:0.72,fontFace:F,fontSize:16,bold:true,color:P,valign:'middle',isTextBox:true,margin:0});
s.addNotes('ここが訪問入浴の医療的価値です。褥瘡の初期発赤を最初に見つけるのは、入浴の場面が非常に多いです。');

/* ---------- 9. Ch4-2 役割分担 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 4','看護師の視点・医療連携','訪問入浴と訪問看護の役割分担');
s.addText(runs('訪問入浴は介護保険サービスであり、**医療行為は行えません**。だからこそ訪問看護との連携が欠かせません。',{fontSize:15,strong:S,color:P}),
  {x:M,y:1.58,w:CW,h:0.42,valign:'middle',isTextBox:true,margin:0});
card(s,{x:M,y:2.14,w:CW/2-0.16,h:2.86,fill:TG,title:'訪問入浴が担うこと',titleColor:S,items:[
 'バイタル測定と**入浴可否の判断**','入浴時の**全身観察**（褥瘡・浮腫・皮膚）',
 '洗身・洗髪と**日常的な保湿ケア**','観察所見の**記録と当日中の報告**'],fontSize:12.5});
card(s,{x:M+CW/2+0.16,y:2.14,w:CW/2-0.16,h:2.86,fill:TINT,title:'訪問看護におつなぎすること',items:[
 '褥瘡・創傷の**処置**、薬剤の塗布','点滴・注射・採血','カテーテル・ストーマの管理',
 '喀痰吸引・経管栄養の管理','医師の指示に基づく**医療的ケア全般**'],fontSize:12.5});
s.addShape(pres.ShapeType.roundRect,{x:M,y:5.18,w:CW,h:0.88,fill:{color:TINT},rectRadius:0.06,line:{color:TINT}});
s.addText([{text:'私たちの役割は',options:{fontFace:F,fontSize:15,color:TX}},
  {text:'「見つけて、つなぐ」',options:{fontFace:F,fontSize:15,bold:true,color:S}},
  {text:'こと。処置は訪問看護へ——この線引きを明確にすることが、安全な在宅ケアにつながります。',options:{fontFace:F,fontSize:15,color:TX}}],
  {x:M+0.28,y:5.18,w:CW-0.56,h:0.88,valign:'middle',lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addNotes('訪問入浴は介護保険サービスなので医療行為はできません。だから訪問看護との連携が前提になります。この線引きを明確にお伝えしてください。');

/* ---------- 10. Ch4-3 連携のお願い ---------- */
s=pres.addSlide();
header(s,'CHAPTER 4','看護師の視点・医療連携','訪問看護のみなさまへ ── 連携のお願い');
const wr=(CW-0.44)/3;
card(s,{x:M,y:1.66,w:wr,h:3.2,fill:TG,title:'① 訪問日を合わせてください',titleColor:S,
  body:'入浴直後は皮膚が清潔で、**創部の観察と処置に最も適した状態**です。同日・入浴後にご訪問いただけると、処置の条件が整います。',fontSize:12.5});
card(s,{x:M+wr+0.22,y:1.66,w:wr,h:3.2,fill:TINT,title:'② 見てほしい部位を',
  body:'前回の**処置内容と注意部位**を共有いただければ、その点を重点的に観察し、当日中に連絡ノート・電話・必要時は写真でお返しします。',fontSize:12.5});
card(s,{x:M+2*(wr+0.22),y:1.66,w:wr,h:3.2,fill:TINT,title:'③ 医療的ケアは事前に相談',
  body:'気管切開・経管栄養・在宅酸素など。**主治医の指示内容と留意点**を共有いただければ、受け入れ可否と入浴時の注意点を一緒に検討します。',fontSize:12.5});
s.addShape(pres.ShapeType.roundRect,{x:M,y:5.04,w:CW,h:0.95,fill:{color:S},rectRadius:0.07,line:{color:S}});
s.addText('「この状態で入浴させてよいか」——迷った時点でご連絡ください。一緒に判断させてください。',
  {x:M+0.3,y:5.04,w:CW-0.6,h:0.95,fontFace:F,fontSize:17,bold:true,color:WH,align:'center',valign:'middle',isTextBox:true,margin:0});
s.addNotes('本日いちばんお願いしたい点です。特に訪問看護ステーションの方に向けて、同日訪問と事前相談をお願いしてください。');

/* ---------- 9. Ch4-2 チーム ---------- */
s=pres.addSlide();
header(s,'CHAPTER 4','看護師の視点・医療連携','在宅チームの一員として');
s.addShape(pres.ShapeType.roundRect,{x:M,y:1.86,w:2.5,h:1.62,fill:{color:S},rectRadius:0.07,line:{color:S}});
s.addText([{text:'訪問入浴介護',options:{fontFace:F,fontSize:16,bold:true,color:WH,breakLine:true}},
  {text:'看護師1名＋介護2名',options:{fontFace:F,fontSize:10.5,color:'D6F3E6'}}],
  {x:M+0.1,y:1.86,w:2.3,h:1.62,align:'center',valign:'middle',lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addText('⇄',{x:M+2.56,y:1.86,w:0.42,h:1.62,fontFace:F,fontSize:22,bold:true,color:S,align:'center',valign:'middle',isTextBox:true,margin:0});
const px=M+3.06, pw=(CW-3.06-0.22)/2;
[['主治医・在宅医','創部・全身状態の報告／指示の確認'],['訪問看護ステーション','観察所見の共有／医療処置の依頼'],
 ['ケアマネジャー','状態変化・生活課題のフィードバック'],['デイサービス・訪問介護','入浴日の分担／スキンケアの継続']]
.forEach((p,i)=>{
  const x=px+(i%2)*(pw+0.22), y=1.86+Math.floor(i/2)*0.86;
  s.addShape(pres.ShapeType.roundRect,{x,y,w:pw,h:0.74,fill:{color:TINT},rectRadius:0.05,line:{color:TINT}});
  s.addText([{text:p[0],options:{fontFace:F,fontSize:13.5,bold:true,color:P,breakLine:true}},
    {text:p[1],options:{fontFace:F,fontSize:10,color:SUB}}],
    {x:x+0.22,y,w:pw-0.44,h:0.74,valign:'middle',lineSpacingMultiple:1.15,isTextBox:true,margin:0});
});
card(s,{x:M,y:3.74,w:CW/2-0.16,h:1.66,fill:TINT,title:'「競合」ではありません',
  body:'デイサービスに通えている間はデイでの入浴を。**体調やADLの低下で通所が難しくなった時期**に訪問入浴が引き継ぐ、という補完関係です。',fontSize:12.5});
card(s,{x:M+CW/2+0.16,y:3.74,w:CW/2-0.16,h:1.66,fill:TG,title:'併用が最も現実的',titleColor:S,
  body:'「デイ入浴＋訪問入浴」「訪問入浴の観察＋訪問看護の処置」。**役割を分け合うことで在宅の限界点が延びます。**',fontSize:12.5});
s.addNotes('デイサービスの方に特にお伝えしたい点です。奪い合いではなく、通所が難しくなった段階での受け皿としてお考えください。');

/* ---------- 10. Ch5 介護報酬 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 5','介護報酬','単位数と主な加算');
const fh=t=>({text:t,options:{fontFace:F,fontSize:12,bold:true,color:WH,valign:'middle',fill:{color:P}}});
const fc=(t,o={})=>({text:t,options:{fontFace:F,fontSize:13,color:TX,valign:'middle',...o}});
const fn=(v,u,o={})=>({text:[{text:v,options:{fontFace:F,fontSize:16,bold:true,color:o.c||P}},
  {text:' '+u,options:{fontFace:F,fontSize:10,color:SUB}}],options:{align:'right',valign:'middle',...o}});
const grp=t=>({text:t,options:{fontFace:F,fontSize:12,bold:true,color:WH,valign:'middle',fill:{color:P}}});
s.addTable([
 [fh('サービス'),{text:'単位数',options:{fontFace:F,fontSize:12,bold:true,color:WH,align:'right',valign:'middle',fill:{color:P}}}],
 [{text:[{text:'訪問入浴介護費',options:{fontFace:F,fontSize:14,bold:true,color:TX}},
   {text:'\n看護師1＋介護2の3名体制・全身浴',options:{fontFace:F,fontSize:9.5,color:SUB}}],options:{valign:'middle',fill:{color:TG}}},
  fn('1,266','単位/回',{c:S,fill:{color:TG}})],
 [fc('清拭（身体介護2・30〜60分）'),fn('387','単位/回')],
 [fc('清拭（身体介護3・1時間以上）'),fn('567','単位/回')],
 [grp('主な加算'),{text:'単位数',options:{fontFace:F,fontSize:12,bold:true,color:WH,align:'right',valign:'middle',fill:{color:P}}}],
 [fc('看取り連携体制加算（2024年新設）'),fn('64','単位')],
 [fc('認知症専門ケア加算（Ⅰ）'),fn('3','単位/日')],
 [fc('認知症専門ケア加算（Ⅱ）'),fn('4','単位/日')]],
 {x:M,y:1.62,w:6.9,colW:[4.75,2.15],rowH:0.42,border:{type:'solid',color:'E5E9EC',pt:1},fontFace:F,valign:'middle'});
s.addText('※2024年4月改定後の単位数。単価は地域区分により異なります。',
  {x:M,y:5.36,w:6.9,h:0.3,fontFace:F,fontSize:10,color:SUB,isTextBox:true,margin:0});
card(s,{x:M+7.16,y:1.62,w:CW-7.16,h:3.62,fill:TG,title:'単位数をどう読むか',titleColor:S,items:[
 '**3名（うち看護職員1名）**が同時に訪問（厚生労働省令で定められた体制）','専用浴槽・給湯設備の**持ち込みと設置**','清拭では届かない**全身浴・洗髪**',
 '毎回の**バイタル測定と全身観察**','関係職種への**情報共有**'],fontSize:12.5});
s.addText(runs('入浴のみの報酬ではなく、**看護アセスメントを含んだ包括的なケアの対価**としてご検討ください。',{fontSize:12.5}),
  {x:M+7.4,y:4.5,w:CW-7.64,h:0.7,lineSpacingMultiple:1.25,isTextBox:true,margin:0});
s.addNotes('単位数が高いという指摘は当然あります。何が含まれているかを分解して説明できるようにしておきます。');

/* ---------- 11. Ch6 声 ---------- */
s=pres.addSlide();
header(s,'CHAPTER 6','利用者・ご家族の声','現場で聞かれる言葉');
[['「毎週のお風呂が楽しみで、それだけで気持ちが前向きになります。」','80代・要介護4・ご本人'],
 ['「一人では絶対に無理でした。プロに任せることで、私も安心して介護できるようになりました。」','60代・ご家族（介護者）']]
.forEach((v,i)=>{
  const y=1.72+i*1.66;
  s.addShape(pres.ShapeType.roundRect,{x:M,y,w:CW,h:1.42,fill:{color:TINT},rectRadius:0.07,line:{color:TINT}});
  s.addText(v[0],{x:M+0.42,y:y+0.14,w:CW-0.84,h:0.74,fontFace:F,fontSize:19,color:TX,valign:'middle',lineSpacingMultiple:1.25,isTextBox:true,margin:0});
  s.addText(v[1],{x:M+0.42,y:y+0.94,w:CW-0.84,h:0.34,fontFace:F,fontSize:12,color:SUB,align:'right',valign:'middle',isTextBox:true,margin:0});
});
s.addText(runs('入浴の効果は清潔だけにとどまりません。**ご本人の意欲と、介護するご家族の負担軽減**——その両方に届くケアです。',{fontSize:15}),
  {x:M,y:5.28,w:CW,h:0.6,lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addNotes('数字では伝わらない部分です。ご家族の負担軽減という側面も強調してください。');

/* ---------- 12. まとめ ---------- */
s=pres.addSlide();
header(s,'SUMMARY','まとめ','訪問入浴介護が担う役割');
s.addText(bullets([
 '**入浴困難の「空白地帯」を埋める**——デイに通えず、清拭では足りない方の受け皿。',
 '**「自宅で・全身浴を・看護師付きで・重度でも」の4条件を唯一満たす**サービス。',
 '**週1〜2回の全身アセスメントの場**——褥瘡・浮腫・栄養状態の変化を早期に捉える。',
 '**医療行為は行わず「見つけて、つなぐ」**——訪問看護と役割を分け合い、その日のうちに情報を共有。'],{fontSize:15,strong:P,color:TX}),
 {x:M,y:1.66,w:CW,h:2.3,paraSpaceAfter:12,valign:'top',isTextBox:true,margin:0});
s.addShape(pres.ShapeType.roundRect,{x:M,y:4.12,w:CW,h:1.35,fill:{color:P},rectRadius:0.07,line:{color:P}});
s.addText([{text:'「もう入浴は難しいかもしれない」と感じた時が、',options:{fontFace:F,fontSize:19,bold:true,color:WH,breakLine:true}},
  {text:'訪問入浴をご検討いただくタイミングです。',options:{fontFace:F,fontSize:19,bold:true,color:MINT}}],
  {x:M+0.35,y:4.12,w:CW-0.7,h:1.35,align:'center',valign:'middle',lineSpacingMultiple:1.3,isTextBox:true,margin:0});
s.addText('導入の可否だけでもご相談ください。状態を伺ったうえで、他サービスとの組み合わせを含めてご提案します。',
  {x:M,y:5.62,w:CW,h:0.4,fontFace:F,fontSize:13,color:SUB,isTextBox:true,margin:0});
s.addNotes('4点に整理しました。最後のメッセージ——迷った段階でご相談いただきたい、を強調して締めます。');

/* ---------- 13. 連絡先 ---------- */
s=pres.addSlide();
s.background={color:P};
s.addText('CONTACT',{x:M,y:0.5,w:3,h:0.32,fontFace:F,fontSize:13,bold:true,color:MINT,charSpacing:2,isTextBox:true,margin:0});
s.addText('連絡先・お問い合わせ',{x:M,y:0.92,w:CW,h:0.6,fontFace:F,fontSize:30,bold:true,color:WH,valign:'middle',isTextBox:true,margin:0});
contactBlock(s,1.86,true);
banner(s,{x:M,y:5.14,w:CW,h:0.86,fill:WH,color:S,text:'まずはご相談から。お気軽にどうぞ。',size:20});
s.addText('初回アセスメントは無料でお伺いします。導入の可否判断からお手伝いします。',
  {x:M,y:6.14,w:CW,h:0.36,fontFace:F,fontSize:12,color:'C9DCE8',align:'center',isTextBox:true,margin:0});
s.addNotes('ご相談は電話が最も早いです。初回アセスメントは無料である点をお伝えください。');

pres.writeFile({fileName:'/home/user/houmonnyuyoku/houmon-nyuyoku-slides.pptx'})
  .then(f=>console.log('written:',f));

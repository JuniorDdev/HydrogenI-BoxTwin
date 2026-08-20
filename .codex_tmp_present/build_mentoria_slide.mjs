import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const TMP_DIR = process.env.TMP_DIR;
const FINAL_PPTX = process.env.FINAL_PPTX;

async function writeBlob(targetPath, blob) {
  await fs.writeFile(targetPath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(TMP_DIR, { recursive: true });

  const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const slide = deck.slides.add();
  slide.background.fill = "#FFFFFF";

  const frame = { left: 72, top: 56, width: 1136, height: 608 };

  const topRule = slide.shapes.add({
    geometry: "rect",
    position: { left: frame.left, top: frame.top, width: frame.width, height: 8 },
    fill: "#3D8DFF",
    line: { style: "solid", fill: "#3D8DFF", width: 0 },
  });
  topRule.name = "top-rule";

  const eyebrow = slide.shapes.add({
    geometry: "textbox",
    position: { left: frame.left, top: frame.top + 24, width: 320, height: 28 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  eyebrow.text = "MENTORIA DIA 1 · TURMA B · 20/08/2026";
  eyebrow.text.style = { fontSize: 16, bold: true, color: "#5F6B7A", fontFace: "Arial" };

  const title = slide.shapes.add({
    geometry: "textbox",
    position: { left: frame.left, top: frame.top + 72, width: 700, height: 130 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  title.text = "HydrogenI automatiza a medição do box e já demonstra o fluxo operacional do MVP";
  title.text.style = { fontSize: 35, bold: true, color: "#111111", fontFace: "Arial" };

  const subtitle = slide.shapes.add({
    geometry: "textbox",
    position: { left: frame.left, top: frame.top + 206, width: 520, height: 96 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  subtitle.text = "Hoje mostramos o protótipo funcional e buscamos validar precisão, contexto operacional e próximos requisitos do ambiente real.";
  subtitle.text.style = { fontSize: 20, color: "#4B5563", fontFace: "Arial" };

  const leftHeading = slide.shapes.add({
    geometry: "textbox",
    position: { left: frame.left, top: frame.top + 336, width: 320, height: 64 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  leftHeading.text = "O que já conseguimos provar";
  leftHeading.text.style = { fontSize: 24, bold: true, color: "#111111", fontFace: "Arial" };

  const leftBody = slide.shapes.add({
    geometry: "textbox",
    position: { left: frame.left, top: frame.top + 404, width: 500, height: 170 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  leftBody.text = "• Leitura simulada do box com cálculo de ocupação e volume\n• Painel local e painel administrativo com alertas e tratativas\n• Histórico de medições, exportação em PDF/Excel e base Raspberry + Railway";
  leftBody.text.style = { fontSize: 18, color: "#222222", fontFace: "Arial", breakLine: true };

  const rightPanel = slide.shapes.add({
    geometry: "rect",
    position: { left: 660, top: frame.top + 88, width: 478, height: 444 },
    fill: "#EDEDED",
    line: { style: "solid", fill: "#D0D5DD", width: 1 },
  });
  rightPanel.name = "question-panel";

  const rightHeading = slide.shapes.add({
    geometry: "textbox",
    position: { left: 692, top: frame.top + 118, width: 390, height: 42 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  rightHeading.text = "O que queremos validar hoje";
  rightHeading.text.style = { fontSize: 28, bold: true, color: "#111111", fontFace: "Arial" };

  const rightBody = slide.shapes.add({
    geometry: "textbox",
    position: { left: 692, top: frame.top + 176, width: 388, height: 270 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  rightBody.text = "1. Qual precisão mínima é aceitável para operação real?\n2. O acompanhamento precisa ser em m³, toneladas ou ambos?\n3. Como poeira, máquinas e rede local afetam a implantação no box?";
  rightBody.text.style = { fontSize: 22, color: "#1F2937", fontFace: "Arial", breakLine: true };

  const footer = slide.shapes.add({
    geometry: "textbox",
    position: { left: 692, top: frame.top + 466, width: 388, height: 46 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  footer.text = "Próximo passo do time: conectar sensor real e validar no ambiente físico.";
  footer.text.style = { fontSize: 18, bold: true, color: "#3D8DFF", fontFace: "Arial" };

  const png = await deck.export({ slide, format: "png", scale: 1 });
  await writeBlob(path.join(TMP_DIR, "slide-1.png"), png);

  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(TMP_DIR, "slide-1.layout.json"), await layout.text(), "utf8");

  const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
  await writeBlob(path.join(TMP_DIR, "deck-montage.webp"), montage);

  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

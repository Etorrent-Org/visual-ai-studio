const $ = (id) => document.getElementById(id);

const preset = {
  instagram: { label: "Instagram", channel: "Instagram Feed", width: 1080, height: 1350, ratio: "4:5" },
  custom: { label: "Autre / personnalisé", channel: "À préciser", width: null, height: null, ratio: "" }
};

const value = (id, fallback = "Non renseigné") => {
  const node = $(id);
  const raw = node ? String(node.value ?? "").trim() : "";
  return raw || fallback;
};

const postStructure = (count) => count <= 1
  ? "1 visuel principal"
  : `${count} visuels principaux cohérents à publier ensemble dans un seul post, avec une narration visuelle commune`;

function buildPrompt() {
  const mode = $("mode").value;
  const p = preset[mode];
  const count = Math.max(1, Math.min(10, Number($("post_image_count").value || 1)));
  const width = mode === "instagram" ? p.width : Number($("target_width").value || 0) || null;
  const height = mode === "instagram" ? p.height : Number($("target_height").value || 0) || null;
  const ratio = mode === "instagram" ? p.ratio : value("aspect_ratio", "À préciser avec Studio Visuel");
  const dimensions = width && height ? `${width} x ${height} px` : "À préciser avec Studio Visuel";
  const referenceNote = value("reference_note", "Aucune référence décrite.");
  const hasReference = referenceNote === "Aucune référence décrite." ? "NON" : "OUI";

  return `INTENTION : CREATION_IMAGE
AGENT CIBLE : Studio Visuel
SORTIE : ${p.label}

PROJET
Titre : ${value("title")}
Collection / campagne : ${value("collection")}

BRIEF
Idée / demande : ${value("raw_idea")}
Objectif : ${value("intent")}
Audience : ${value("audience")}
Sujet principal : ${value("subject")}
Style : ${value("style")}
Décor : ${value("setting")}
Ambiance : ${value("ambience")}
Palette : ${value("palette")}
Lumière : ${value("lighting")}
Matières : ${value("materials")}
Composition : ${value("composition")}
Niveau de détail : ${value("detail_level")}
Éléments obligatoires : ${value("required_elements", "Aucun")}
Éléments interdits : ${value("forbidden_elements", "Aucun")}
Texte demandé dans l'image : ${value("text_overlay", "Aucun")}

PUBLICATION
Nombre de visuels principaux : ${count}
Structure : ${postStructure(count)}
Les visuels principaux appartiennent à une seule publication et doivent rester cohérents entre eux.
Pour Instagram, les visuels finaux signés doivent être livrés en JPEG/JPG réel ; le PNG est accepté uniquement comme source intermédiaire.
Après validation des visuels, la fiche de synthèse PNG et le Markdown IA-Art sont des livrables obligatoires, séparés des visuels principaux et non comptés dans leur nombre.

FORMAT
Canal : ${p.channel}
Dimensions par visuel principal : ${dimensions}
Ratio : ${ratio}

RÉFÉRENCE
Image de référence : ${hasReference}
Note de référence : ${referenceNote}

NOTES
${value("notes", "Aucune")}

INSTRUCTION DE DÉMARRAGE

Utilise le Skill \`visual-content-studio\` comme source de vérité.

Traite cette demande comme une création d'image.

Respecte le workflow conversationnel de Studio Visuel :
- une seule étape par réponse ;
- validation explicite avant l'étape suivante ;
- aucune génération d'image avant validation du brief et de la direction artistique ;
- aucun branding, logo, watermark ou signature non demandé ;
- aucun texte ajouté dans l'image sauf demande explicite ci-dessus ;
- si plusieurs visuels principaux sont demandés, conçois-les comme une série cohérente destinée à un seul post, et non comme des variantes indépendantes ;
- les PNG affichés par image_gen sont uniquement des sources intermédiaires et ne doivent jamais être présentés comme la livraison finale ;
- juste avant image_gen, indique que je dois répondre simplement continue dès que les PNG sont affichés ;
- à mon message continue (ou équivalent bref), reprends directement après la génération, sans refaire les étapes créatives, puis poursuis dans le même tour jusqu'au paquet IA-Art complet : N JPEG/JPG signés + 1 synthèse PNG + 1 Markdown + archive.

Commence maintenant par l'Étape 1 — Brief.

Reformule le brief et attends ma validation avant de poursuivre.
`;
}

function showPrompt(prompt) {
  $("prompt-output").textContent = prompt;
  $("prompt-output").classList.remove("hidden");
  $("empty-prompt").classList.add("hidden");
  $("prompt-actions").classList.remove("hidden");
  $("prompt-state").textContent = "Prêt";
}

$("mode").addEventListener("change", () => {
  $("custom-format").classList.toggle("hidden", $("mode").value !== "custom");
});

$("brief-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!value("title", "") || !value("raw_idea", "")) {
    $("prompt-state").textContent = "Brief incomplet";
    return;
  }
  showPrompt(buildPrompt());
});

$("copy-btn").addEventListener("click", async () => {
  await navigator.clipboard.writeText($("prompt-output").textContent);
  const original = $("copy-btn").textContent;
  $("copy-btn").textContent = "Copié ✓";
  setTimeout(() => $("copy-btn").textContent = original, 1300);
});

$("download-btn").addEventListener("click", () => {
  const content = $("prompt-output").textContent;
  const slug = value("title", "ia-art").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${slug || "ia-art"}-prompt.txt`;
  anchor.click();
  URL.revokeObjectURL(url);
});

$("reset-btn").addEventListener("click", () => {
  $("brief-form").reset();
  $("post_image_count").value = "1";
  $("custom-format").classList.add("hidden");
  $("prompt-output").textContent = "";
  $("prompt-output").classList.add("hidden");
  $("prompt-actions").classList.add("hidden");
  $("empty-prompt").classList.remove("hidden");
  $("prompt-state").textContent = "En attente";
});

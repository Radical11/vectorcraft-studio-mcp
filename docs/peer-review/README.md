# Academic manuscript and future algorithm proposal

**Preserving design intent in agent assisted vector graphics** is a 20-page research-style report for college peer review. It is not a peer-reviewed publication. It documents the released companion and its limited case evidence, then specifies an **unimplemented** coarse-to-fine proposal and an **unrun** 54-output evaluation.

- [Public PDF](paper-public.pdf) and [editable DOCX](paper-public.docx)
- [Editable manuscript source](manuscript.md)
- [Numbered bibliography and access status](bibliography.json), [BibTeX](bibliography.bib)
- [Claim to evidence index](evidence-index.json)
- [Peer review questionnaire](questionnaire.md)
- [Prospective evidence record examples](future-records.json) and [document verification](verification.json)
- [Public document checksums](SHA256SUMS.txt)
- [Original SVG figures and derived PNGs](figures/)
- [Showcase](https://radical11.github.io/vectorcraft-studio-mcp/peer-review.html)
- [Existing alpha release](https://github.com/Radical11/vectorcraft-studio-mcp/releases/tag/v3.1.0-alpha.1)

The blind DOCX/PDF are supplied separately for anonymous review and excluded from the public repository. Both editions come from the same Markdown body and bibliography. The blind builder removes identifying owned links and author metadata. Publicly recognizable artwork can still compromise practical blinding; the paper does not claim perfect anonymity.

## Figures and provenance

Eight original technical SVGs explain the timeline, architecture, workflow, revision invalidation, proposed pipeline, semantic hierarchy, relationship/dependency distinction, and retained-best logic. Their filename numbers identify the requested diagram set, while manuscript captions follow appearance order. The proposed pipeline and repair graphs are conceptual. PNGs are render derivatives for Word compatibility. Three comparison PNGs compose unchanged released intended-size previews side by side; print scaling is disclosed. Source artwork and its attribution remain in examples/ and ASSETS.md. No publisher figures or upstream branding assets are included.

## Rebuild

Document authoring requires Python with python-docx and Pillow, Node with sharp, LibreOffice, and Poppler. These are document-development dependencies, not requirements of the companion runtime. The verified build used the Codex bundled artifact runtime; resolve its paths with the desktop workspace dependency loader. Run from the repository root:

```powershell
python docs/peer-review/build.py --node <node-executable> --node-modules <node-modules-directory>
```

This creates public DOCX, blind DOCX under outputs/peer-review/, eight SVG/PNG pairs, and BibTeX. It does not invoke the editor, alter gateway code, install configuration, or run the proposed algorithm. Re-encode comparison previews only to strip metadata; their visual pixels are unchanged.

Render both editions with the document runtime's render_docx.py, with LibreOffice on the process PATH, using --emit_pdf. Inspect every page before replacing distributed PDFs. Build environments can change pagination; the delivered PDFs are the verified 20-page records. PDF cleanup and audits are available in finalize.py, which expects the renderer outputs and does not claim visual inspection from automated checks. Public copies contain no author names; literature authors are properly attributed in the references.

## Interpretation

The historical Windows suite comprises 124 checks, including 113 self-contained checks. Hosted Linux CI verifies the latter and packaging, not Windows native integration or artistic quality. The release comparisons are creator-authored case studies reviewed by fresh same-model contexts and one owner. They are not a controlled human study. Historical losses, research coverage limits, and remaining repair anatomy problems are disclosed. The existing alpha tag and downloads are preserved; this manuscript is a documentation update on main.

Owned manuscript text and diagrams use MIT OR Apache-2.0, consistent with the repository. Third-party work is cited, not redistributed. The maintainer proposal remains unsent.

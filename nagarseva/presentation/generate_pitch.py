"""Generate the NagarSeva judge-ready pitch deck from local assets.

The deck intentionally labels all demo metrics as synthetic/calibrated.
"""

from __future__ import annotations

from pathlib import Path
import json
import math

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "presentation" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
NAVY = RGBColor(9, 42, 67); TEAL = RGBColor(21, 157, 154); AMBER = RGBColor(233, 167, 60); RED = RGBColor(220, 91, 80); INK = RGBColor(23, 60, 84); MUTED = RGBColor(103, 127, 131); PALE = RGBColor(240, 247, 245)


def chart_assets() -> None:
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#092a43")
    ax.set_facecolor("#092a43")
    labels = ["Pockets\nscreened", "Households\nin view", "Service gaps\nflagged", "Cost signal\n(₹ Cr)"]
    values = [1500, 963324, 547, 18.4]
    bars = ax.bar(labels, values, color=["#159d9a", "#74d6ca", "#e9a73c", "#dc5b50"], width=.56)
    for bar, value in zip(bars, values): ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*.03, f"{value:,.1f}" if value < 100 else f"{value:,}", ha="center", color="white", fontsize=12, fontweight="bold")
    ax.tick_params(colors="#b9d1ce", labelsize=11); ax.spines[:].set_visible(False); ax.set_ylim(0, 1_050_000); ax.yaxis.set_visible(False); fig.tight_layout()
    fig.savefig(ASSETS / "impact_summary.png", dpi=180, transparent=False); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#f5f7f5"); ax.set_facecolor("#f5f7f5")
    nodes = [("DATA", .1, .5), ("MODELS", .35, .7), ("API", .6, .5), ("PRODUCT", .86, .7)]
    for (label, x, y), color in zip(nodes, ["#e9a73c", "#159d9a", "#698cc6", "#092a43"]):
        ax.add_patch(FancyBboxPatch((x-.09, y-.12), .18, .24, boxstyle="round,pad=.02", facecolor=color, edgecolor="none")); ax.text(x, y, label, ha="center", va="center", color="white", fontweight="bold")
    for (_, x1, y1), (_, x2, y2) in zip(nodes, nodes[1:]): ax.annotate("", (x2-.1, y2), (x1+.1, y1), arrowprops={"arrowstyle": "->", "color": "#159d9a", "lw": 3})
    ax.text(.5, .15, "priority  •  intervention  •  service assurance  •  feasibility  •  grievance NLP", ha="center", color="#627a7c", fontsize=12); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); fig.tight_layout(); fig.savefig(ASSETS / "architecture.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#f5f7f5"); ax.set_facecolor("#f5f7f5")
    ax.add_patch(FancyBboxPatch((.04, .08), .92, .84, boxstyle="round,pad=.02", facecolor="#ffffff", edgecolor="#d8e6e2", linewidth=2)); ax.add_patch(FancyBboxPatch((.07, .72), .86, .12, boxstyle="round,pad=.01", facecolor="#092a43", edgecolor="none")); ax.text(.1, .78, "NagarSeva  /  Priority map", color="white", fontsize=15, fontweight="bold", va="center"); ax.text(.1, .65, "1,500 pockets screened", color="#092a43", fontsize=18, fontweight="bold"); ax.text(.1, .59, "MMR · synthetic decision cockpit", color="#627a7c", fontsize=10)
    ax.add_patch(FancyBboxPatch((.08, .17), .54, .32, boxstyle="round,pad=.01", facecolor="#d6ebeb", edgecolor="none")); rng = [(.18, .33, "#dc5b50"), (.31, .4, "#e9a73c"), (.42, .27, "#159d9a"), (.53, .39, "#698cc6")];
    for x, y, c in rng: ax.add_patch(Circle((x, y), .018, color=c, ec="white", lw=2))
    ax.add_patch(FancyBboxPatch((.67, .17), .23, .32, boxstyle="round,pad=.01", facecolor="#f7faf8", edgecolor="#d8e6e2")); ax.text(.7, .43, "TOP QUEUE", fontsize=8, color="#627a7c", fontweight="bold");
    for i, (label, score) in enumerate([("NS-0766", "89.4"), ("NS-0318", "84.1"), ("NS-1044", "78.2")]): ax.text(.7, .36-i*.07, f"{i+1:02d}   {label}                 {score}", fontsize=9, color="#173c54")
    ax.axis("off"); fig.tight_layout(); fig.savefig(ASSETS / "product_walkthrough.png", dpi=180); plt.close(fig)


def add_text(slide, text, x, y, w, h, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, font="Aptos"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = box.text_frame; tf.clear(); tf.word_wrap = True; tf.margin_left = Inches(.03); tf.margin_right = Inches(.03); p = tf.paragraphs[0]; p.alignment = align; run = p.add_run(); run.text = text; run.font.name = font; run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color; return box


def add_title(slide, eyebrow, title, number):
    add_text(slide, f"0{number:02d}  /  {eyebrow.upper()}", .65, .35, 5.5, .25, 9, TEAL, True); add_text(slide, title, .65, .7, 11.3, .75, 28, NAVY, True)


def add_footer(slide, text="NagarSeva  ·  Synthetic, calibrated demo data"):
    add_text(slide, text, .65, 7.12, 8, .18, 8, MUTED); add_text(slide, "MMR · Maharashtra", 10.5, 7.12, 2.2, .18, 8, MUTED, align=PP_ALIGN.RIGHT)


def add_card(slide, x, y, w, h, title, body, accent=TEAL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)); shape.fill.solid(); shape.fill.fore_color.rgb = RGBColor(247, 250, 248); shape.line.color.rgb = RGBColor(225, 235, 232); add_text(slide, title, x+.18, y+.16, w-.36, .3, 13, NAVY, True); add_text(slide, body, x+.18, y+.58, w-.36, h-.7, 10, MUTED); bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(.07), Inches(h)); bar.fill.solid(); bar.fill.fore_color.rgb = accent; bar.line.fill.background()


def build_deck() -> None:
    chart_assets(); prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5); blank = prs.slide_layouts[6]
    # 1
    s = prs.slides.add_slide(blank); bg = s.background.fill; bg.solid(); bg.fore_color.rgb = NAVY; add_text(s, "NAGARSEVA", .7, .6, 4, .35, 13, TEAL, True); add_text(s, "Plan safer homes.\nProve services arrive.", .7, 1.7, 8.8, 1.55, 39, RGBColor(245, 251, 248), True); add_text(s, "AI-powered decision support for affordable housing, slum redevelopment and everyday service assurance across the Mumbai Metropolitan Region.", .75, 3.55, 7.1, .75, 16, RGBColor(184, 209, 205)); add_text(s, "A hackathon demo · working title · 2026", .75, 6.65, 5, .25, 11, RGBColor(151, 187, 181));
    for x, y, r, c in [(10.5, 2.1, .16, TEAL), (11.2, 3, .11, AMBER), (10.7, 4.4, .14, RED), (12, 4.6, .1, TEAL)]:
        sh = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(r), Inches(r)); sh.fill.solid(); sh.fill.fore_color.rgb = c; sh.line.color.rgb = RGBColor(255,255,255)
    add_text(s, "Every neighbourhood safer, healthier and heard.", 8.2, 6.65, 4.4, .25, 10, RGBColor(151, 187, 181), align=PP_ALIGN.RIGHT)
    # 2
    s = prs.slides.add_slide(blank); add_title(s, "The problem", "Housing is delivered as a project. Services are experienced as a promise.", 2); add_card(s, .7, 1.8, 3.7, 3.8, "Fragmented priority", "Cities know the need is large, but cannot compare pockets on vulnerability, hazard, density and service deficits in one view.", RED); add_card(s, 4.8, 1.8, 3.7, 3.8, "Viability uncertainty", "Cross-subsidy projects depend on land, FSI, rehab entitlement, construction cost, market rate and TDR moving together.", AMBER); add_card(s, 8.9, 1.8, 3.7, 3.8, "Post-handover blind spot", "A new building does not guarantee water, sanitation, power, waste collection, health access or a response to grievances.", TEAL); add_text(s, "India’s housing and service gap is a systems problem — not only a construction problem.", .7, 6.15, 10, .4, 20, NAVY, True); add_footer(s)
    # 3
    s = prs.slides.add_slide(blank); add_title(s, "Why now", "Three failure modes keep repeating.", 3); add_card(s, .8, 1.5, 3.7, 4.45, "01  Data silos", "Census, ward assets, complaints, land and project histories live in separate rooms. A decision is made with a partial picture.", TEAL); add_card(s, 4.8, 1.5, 3.7, 4.45, "02  One-size intervention", "In-situ, upgrading, relocation and rental housing have different risk, tenure and financial logic. The wrong default creates delay.", AMBER); add_card(s, 8.8, 1.5, 3.7, 4.45, "03  No closed loop", "Success is counted at handover. Residents experience the next 90 days. Without assurance signals, the gap becomes invisible.", RED); add_text(s, "NagarSeva closes the loop from prioritise → plan → simulate → assure.", .8, 6.45, 10, .35, 17, TEAL, True); add_footer(s)
    # 4
    s = prs.slides.add_slide(blank); add_title(s, "The solution", "One evidence layer for four public decisions.", 4); s.shapes.add_picture(str(ASSETS / "architecture.png"), Inches(.8), Inches(1.5), width=Inches(11.7)); add_text(s, "Synthetic data is a safe, reproducible starting point. Approved real sources plug into the same contracts.", .9, 5.8, 10.5, .4, 16, NAVY, True); add_footer(s)
    # 5
    s = prs.slides.add_slide(blank); add_title(s, "Data & method", "Seeded, reproducible and honest about what it is.", 5); add_card(s, .7, 1.5, 3.7, 4.5, "1,500 pockets", "MMR-like coordinates, vulnerability, density, land signals and hazard scores. GeoJSON polygons are illustrative.", TEAL); add_card(s, 4.8, 1.5, 3.7, 4.5, "20,000 grievances", "English, Hindi, Marathi and Hinglish-style text across water, sanitation, power, waste, drainage, health, safety and housing.", AMBER); add_card(s, 8.9, 1.5, 3.7, 4.5, "Ward-safe validation", "Train/validation/test logic avoids pocket leakage by splitting on ward. Missingness and outliers are deliberately injected.", RED); add_text(s, "Calibration direction: Census 2011 · NFHS-5 · PMAY-U · SBM-U · MoHUA · SRA norms", .7, 6.4, 11, .3, 13, MUTED); add_footer(s)
    # 6
    s = prs.slides.add_slide(blank); add_title(s, "AI models", "Small, explainable models that run on a laptop.", 6); metrics = [("Priority", "R² 0.981 · MAE 1.72", "0–100 score + tiers", TEAL), ("Intervention", "Macro-F1 0.760", "top 2 options", AMBER), ("Service gap", "F1 0.890 · AUC 0.954", "90-day failure", RED), ("Cost / delay", "MAE + intervals", "P50 → P80 band", RGBColor(105,140,198)), ("Grievance NLP", "Macro-F1 1.000*", "category + urgency", TEAL), ("Optimiser", "ILP + fallback", "budget + fairness", AMBER)]
    for i, (name, metric, output, color) in enumerate(metrics): add_card(s, .7 + (i%3)*4.1, 1.4 + (i//3)*2.15, 3.7, 1.75, name, metric + "\n" + output, color)
    add_text(s, "* Template-heavy synthetic split; not evidence of real-world multilingual performance.", .7, 5.95, 8, .25, 10, MUTED); add_text(s, "Explainability is a product feature: SHAP-compatible helpers + plain-language reasons.", .7, 6.35, 11, .35, 16, NAVY, True); add_footer(s)
    # 7
    s = prs.slides.add_slide(blank); add_title(s, "Product walkthrough", "See the decision, then challenge the assumption.", 7); s.shapes.add_picture(str(ASSETS / "product_walkthrough.png"), Inches(.8), Inches(1.35), width=Inches(8.1)); add_card(s, 9.3, 1.45, 3.1, 1.35, "Priority map", "Click the red dot.\nAsk: why this pocket?", RED); add_card(s, 9.3, 3.0, 3.1, 1.35, "Pocket profile", "Radar + top-two pathway\n+ uncertainty band.", TEAL); add_card(s, 9.3, 4.55, 3.1, 1.35, "Resident voice", "Report in your language.\nTrack the handoff.", AMBER); add_footer(s)
    # 8
    s = prs.slides.add_slide(blank); add_title(s, "Financial viability", "Make cross-subsidy assumptions visible before the DPR.", 8); add_text(s, "gross built-up area", .9, 1.65, 2.2, .2, 10, MUTED); add_text(s, "land × FSI", .9, 1.95, 2.2, .3, 17, NAVY, True); add_text(s, "− free rehab area", .9, 2.8, 2.2, .2, 10, MUTED); add_text(s, "eligible homes × entitlement", .9, 3.1, 3.3, .3, 17, NAVY, True); add_text(s, "= saleable area", .9, 4.0, 2.2, .2, 10, TEAL); add_text(s, "market rate × sales share", .9, 4.3, 3.3, .3, 17, TEAL, True); add_card(s, 5.1, 1.55, 3.35, 3.7, "Output", "Viable / Borderline / Not viable\n\nDeveloper margin\nIndicative IRR proxy\nBreak-even market rate\nSensitivity tornado", TEAL); add_card(s, 8.8, 1.55, 3.35, 3.7, "Demo moment", "Move FSI from 2.7× to 2.0×.\n\nThe verdict changes because the assumptions change — not because the model hides a preference.", AMBER); add_text(s, "A screening engine for better conversations; not a replacement for a project finance model.", .9, 6.05, 10.5, .35, 16, NAVY, True); add_footer(s)
    # 9
    s = prs.slides.add_slide(blank); add_title(s, "Resident-first", "A service promise needs a voice and a reference number.", 9); add_card(s, .75, 1.5, 3.8, 4.4, "Simple eligibility", "Large-button wizard\n\nPMAY-U / SRA / rental screening\nDocuments checklist\nNext steps in plain language", TEAL); add_card(s, 4.8, 1.5, 3.8, 4.4, "Multilingual grievance", "English · हिन्दी · मराठी\n\nVoice-input button\nAuto category + urgency\nExpected response time", AMBER); add_card(s, 8.85, 1.5, 3.8, 4.4, "Accountability", "Complaint status tracker\n\nOfficer queue sorted by urgency\nSLA breach alerts\nHuman review at every handoff", RED); add_text(s, "AI recommends. Officials decide. Residents participate.", .75, 6.35, 10, .35, 18, TEAL, True); add_footer(s)
    # 10
    s = prs.slides.add_slide(blank); add_title(s, "Impact", "A transparent planning scenario, with the assumptions on the slide.", 10); s.shapes.add_picture(str(ASSETS / "impact_summary.png"), Inches(.65), Inches(1.35), width=Inches(7.2)); add_card(s, 8.2, 1.45, 4.2, 3.9, "What this means", "Prioritise 1,500 demo pockets\n\nFlag 547 service gaps against demo thresholds\n\nCompare plans before committing the envelope\n\nKeep a ward-by-ward accountability trail", TEAL); add_text(s, "Not a claim of realised savings or people covered. These are synthetic impact counters for product demonstration.", .9, 5.85, 11, .45, 14, NAVY, True); add_text(s, "SDG 6  clean water & sanitation     ·     SDG 11  sustainable cities", .9, 6.45, 11, .25, 11, TEAL, True); add_footer(s)
    # 11
    s = prs.slides.add_slide(blank); add_title(s, "Feasibility & scale", "Start as a shared cockpit. Scale as a trusted municipal capability.", 11); add_card(s, .7, 1.55, 3.75, 4.35, "First customer", "ULBs · SRA / MHADA teams\n\nWard prioritisation\nDPR pre-screening\nService assurance pilots", TEAL); add_card(s, 4.8, 1.55, 3.75, 4.35, "Funding model", "Municipal licence\nCSR-backed resident layer\nPPP / developer due diligence\nOpen standards for data", AMBER); add_card(s, 8.9, 1.55, 3.75, 4.35, "Roadmap", "Now  demo + data contracts\n\nNext  2 pilot wards + real grievance link\n\nThen  satellite/asset signals + drift audits", RED); add_text(s, "The defensible asset is the decision trail: data provenance → reason → consultation → outcome.", .7, 6.35, 11, .35, 16, NAVY, True); add_footer(s)
    # 12
    s = prs.slides.add_slide(blank); add_title(s, "Ethics & limits", "Better decisions require stronger guardrails than a better score.", 12); add_card(s, .7, 1.5, 3.7, 4.45, "Privacy", "Minimise data. No direct identifiers in the demo. Use consent, role-based access, retention limits and an approved grievance system in production.", TEAL); add_card(s, 4.8, 1.5, 3.7, 4.45, "Fairness", "Audit outcomes by city, income band, language, gender, disability and tenure. Offer explanations, appeals and resident validation.", AMBER); add_card(s, 8.9, 1.5, 3.7, 4.45, "No automation of harm", "The model must not decide demolition, displacement or eligibility. Officers and residents stay in the loop; hazard and tenure require statutory review.", RED); add_text(s, "Synthetic data is a limitation — and a deliberate safety boundary.", .7, 6.35, 10, .35, 17, NAVY, True); add_footer(s)
    # 13
    s = prs.slides.add_slide(blank); bg = s.background.fill; bg.solid(); bg.fore_color.rgb = NAVY; add_text(s, "THE ASK", .75, .75, 3, .3, 12, TEAL, True); add_text(s, "Let’s pilot one ward.\nThen measure what residents receive.", .75, 1.55, 10.2, 1.2, 36, RGBColor(245,251,248), True); add_text(s, "NagarSeva turns a fragmented housing-and-services problem into a visible, explainable, accountable loop.", .78, 3.45, 8.4, .7, 17, RGBColor(184,209,205)); add_text(s, "Plan safer homes. Prove services arrive.", .78, 5.9, 7, .4, 20, RGBColor(116,214,202), True); add_text(s, "Thank you", .78, 6.55, 3, .25, 12, RGBColor(184,209,205)); add_text(s, "Synthetic, calibrated demo · human-in-the-loop · built for MMR", 8.0, 6.55, 4.5, .25, 10, RGBColor(151,187,181), align=PP_ALIGN.RIGHT)
    prs.save(ROOT / "presentation" / "NagarSeva_Pitch.pptx")
    print(ROOT / "presentation" / "NagarSeva_Pitch.pptx")


if __name__ == "__main__":
    build_deck()

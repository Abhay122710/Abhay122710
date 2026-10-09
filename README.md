import os, zipfile, textwrap, xml.etree.ElementTree as ET
from pathlib import Path

root = Path("/mnt/data/abhay-github-profile")
assets = root / "assets"
assets.mkdir(parents=True, exist_ok=True)

# Since the two personal PNGs are not attached in this conversation, build an honest scaffold
# that preserves the required filenames and clearly marks the two image slots as pending.
readme = """# Abhay Chaudhary · GitHub Profile

<!--
Before publishing:
1. Add your actual id.png and right_pointing.png to assets/.
2. Replace the image placeholders in the SVGs with embedded PNG data to make them fully self-contained.
3. Add your real social URLs in the Connect section below.
-->

![Animated introduction](./assets/hero.svg?v=1)

![About and interests](./assets/about-life.svg?v=1)

![Technology stack](./assets/stack.svg?v=1)

![Developer ID card](./assets/id-dashboard.svg?v=1)

![Connect](./assets/connect.svg?v=1)

## Selected projects

- **Mnemosyne** — [Open project](https://mnemosyne-eosin.vercel.app/)
- **Vendor Plus** — [Open project](https://vendorplus.online/)
- **Geometry Dash Game** — [Open game](https://abhay122710.itch.io/geometry-dash-game)

## Connect

Social links will be added once the exact URLs are provided.

---

*B.Tech CSE student specializing in Graphics & Gaming at UPES Dehradun.*
"""
(root / "README.md").write_text(readme, encoding="utf-8")

# SVGs are functional visual scaffolds. They avoid inventing a portrait or social details.
common = """<style>
  .bg{fill:#070b16}.panel{fill:#0e1728;stroke:#243650;stroke-width:1.5}
  .white{fill:#f5f7ff}.muted{fill:#a9b5cc}.blue{fill:#247bff}.red{fill:#ff354f}
  .mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
  .display{font-family:Arial,Helvetica,sans-serif;font-weight:800}
  @media(prefers-reduced-motion:reduce){.anim{animation:none!important}}
  .anim{animation:fadein 1.2s ease both}
  @keyframes fadein{from{opacity:.25;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
</style>"""
def svg_doc(body, width=900, height=280):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>Abhay Chaudhary GitHub profile graphic</title>{common}<rect class="bg" width="100%" height="100%" rx="18"/>{body}</svg>'''

svgs = {
"hero.svg": svg_doc("""
<g class="anim">
<text x="42" y="44" class="mono blue" font-size="14">HELLO, WORLD / DEVELOPER PROFILE</text>
<text x="42" y="105" class="display white" font-size="43">Abhay Chaudhary</text>
<text x="42" y="142" class="white" font-size="19">Aspiring Software Developer</text>
<text x="42" y="174" class="muted" font-size="16">B.Tech CSE · Graphics &amp; Gaming · UPES Dehradun</text>
<text x="42" y="204" class="muted" font-size="15">Game development · UI/UX · 3D graphics</text>
<rect x="42" y="226" width="8" height="8" rx="4" class="red"/>
<text x="60" y="235" class="mono muted" font-size="13">DEHRADUN, INDIA</text>
<rect x="650" y="30" width="210" height="220" rx="16" class="panel"/>
<rect x="675" y="55" width="160" height="170" rx="12" fill="#111d31" stroke="#247bff" stroke-dasharray="5 5"/>
<text x="755" y="125" text-anchor="middle" class="blue display" font-size="17">IMAGE SLOT</text>
<text x="755" y="149" text-anchor="middle" class="muted mono" font-size="12">id.png</text>
<text x="755" y="171" text-anchor="middle" class="muted" font-size="11">Add your portrait</text>
</g>"""),
"about-life.svg": svg_doc("""
<text x="36" y="43" class="mono blue" font-size="14">01 / ABOUT &amp; INTERESTS</text>
<text x="36" y="82" class="display white" font-size="28">Curious by design.</text>
<text x="36" y="112" class="muted" font-size="16">Building, experimenting, and learning across creative technology.</text>
<g class="anim">
<rect x="36" y="145" width="250" height="90" rx="14" class="panel"/><text x="56" y="178" class="red display" font-size="18">GAME DEV</text><text x="56" y="204" class="muted" font-size="14">Interactive worlds &amp; mechanics</text>
<rect x="325" y="145" width="250" height="90" rx="14" class="panel"/><text x="345" y="178" class="blue display" font-size="18">UI / UX</text><text x="345" y="204" class="muted" font-size="14">Interfaces &amp; user experiences</text>
<rect x="614" y="145" width="250" height="90" rx="14" class="panel"/><text x="634" y="178" class="red display" font-size="18">3D GRAPHICS</text><text x="634" y="204" class="muted" font-size="14">Visuals, modeling &amp; design</text>
</g>"""),
"stack.svg": svg_doc("""
<text x="36" y="43" class="mono blue" font-size="14">02 / TOOLBOX</text>
<text x="36" y="82" class="display white" font-size="28">Creative + technical</text>
<text x="36" y="112" class="muted" font-size="15">Starter categories — keep only tools you can confidently discuss.</text>
""" + "".join(f'<rect x="{36+(i%4)*211}" y="{145+(i//4)*58}" width="185" height="40" rx="12" class="panel"/><text x="{128+(i%4)*211}" y="{170+(i//4)*58}" text-anchor="middle" class="white" font-size="15">{label}</text>' for i,label in enumerate(["Programming","Game Development","3D Graphics","UI / UX Design","Web Development","Version Control","Problem Solving","Prototyping"]))),
"id-dashboard.svg": svg_doc("""
<g class="anim">
<path d="M440 0 V34" stroke="#77859d" stroke-width="5"/><rect x="405" y="27" width="70" height="25" rx="7" fill="#9aa6b9"/><rect x="250" y="45" width="400" height="205" rx="20" class="panel"/>
<rect x="270" y="65" width="135" height="160" rx="12" fill="#111d31" stroke="#247bff" stroke-dasharray="5 5"/>
<text x="337" y="130" text-anchor="middle" class="blue display" font-size="15">IMAGE SLOT</text><text x="337" y="152" text-anchor="middle" class="muted mono" font-size="12">id.png</text>
<text x="430" y="88" class="mono red" font-size="12">DEVELOPER ID</text><text x="430" y="119" class="display white" font-size="23">Abhay Chaudhary</text>
<text x="430" y="146" class="muted" font-size="13">Aspiring Software Developer</text><text x="430" y="171" class="muted" font-size="13">UPES · Graphics &amp; Gaming</text>
<path d="M430 194 H615" stroke="#243650" stroke-width="2"/><text x="430" y="216" class="mono blue" font-size="11">PROFILE ASSET / IMAGE PENDING</text>
</g>"""),
"connect.svg": svg_doc("""
<text x="36" y="43" class="mono blue" font-size="14">03 / CONNECT</text>
<text x="36" y="82" class="display white" font-size="28">Let's build something.</text>
<rect x="36" y="108" width="240" height="140" rx="15" class="panel"/>
<text x="156" y="157" text-anchor="middle" class="blue display" font-size="17">IMAGE SLOT</text><text x="156" y="181" text-anchor="middle" class="muted mono" font-size="12">right_pointing.png</text>
<path d="M295 174 H350 l-12 -10 m12 10 l-12 10" fill="none" stroke="#ff354f" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="375" y="108" width="480" height="60" rx="14" class="panel"/><text x="398" y="133" class="white display" font-size="16">GitHub</text><text x="398" y="153" class="muted" font-size="13">github.com/abhay122710</text>
<rect x="375" y="188" width="480" height="60" rx="14" class="panel"/><text x="398" y="213" class="white display" font-size="16">Social links</text><text x="398" y="233" class="muted" font-size="13">Exact URLs needed before adding platforms</text>
""")
}
for name, content in svgs.items():
    (assets / name).write_text(content, encoding="utf-8")

preview = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Abhay — GitHub Profile Preview</title>
<style>body{margin:0;padding:24px;background:#070b16;color:#f5f7ff;font:16px Arial,sans-serif;max-width:1000px;margin-inline:auto}h1{color:#247bff}img{display:block;width:100%;height:auto;margin:18px 0;border-radius:18px}p{color:#a9b5cc}</style></head>
<body><h1>Abhay Chaudhary</h1><p>Local preview of the profile SVGs. Image slots are placeholders until the original PNGs are supplied.</p>
""" + "".join(f'<img src="assets/{n}" alt="{n}">' for n in svgs) + "</body></html>"
(root / "preview.html").write_text(preview, encoding="utf-8")

setup = """# Setup instructions

## Important: finish the image slots first
The original `id.png` and `right_pointing.png` were not attached when this starter package was created. The SVGs therefore contain visible placeholders; they do not redraw your identity. Upload the two original PNGs and embed them in the SVGs before treating the package as final.

## Upload to GitHub
1. Open https://github.com/abhay122710/abhay122710. If the repository does not exist, create a **Public** repository named exactly `abhay122710` and initialize it with a README.
2. Unzip this package on your computer.
3. Open the repository and choose **Add file → Upload files**.
4. Upload `README.md` and the complete `assets/` folder, preserving the folder structure.
5. Commit the changes to the default branch.
6. Visit https://github.com/abhay122710 and check that the images render.

`preview.html` is for local preview and `README-SETUP.md` is an instruction file; neither is required in the profile repository.

## Add social links
No social URLs were provided, so the README does not invent any. Add only your exact public profile URLs once ready.
"""
(root / "README-SETUP.md").write_text(setup, encoding="utf-8")

# Validate XML, image path wiring, and supplied URLs syntactically.
for p in assets.glob("*.svg"):
    ET.parse(p)
assert all(f"./assets/{n}?v=1" in readme for n in svgs)
assert "https://mnemosyne-eosin.vercel.app/" in readme
assert "https://vendorplus.online/" in readme
assert "https://abhay122710.itch.io/geometry-dash-game" in readme

zip_path = Path("/mnt/data/abhay-github-profile-starter.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(root.parent))

print("Created:", zip_path)
print("Files:")
for p in sorted(root.rglob("*")):
    if p.is_file():
        print("-", p.relative_to(root))
print("Validation: all SVG files parsed as XML; README image references and project URLs checked.")


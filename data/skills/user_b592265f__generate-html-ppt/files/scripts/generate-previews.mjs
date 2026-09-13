import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const outputDir = path.resolve('demo/previews');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const templates = [
  {
    slug: 'editorial-forest',
    title: 'Q3 Sustainable Architecture & Forestry Review',
    subtitle: 'Preserving Natural Ecosystems Through Adaptive Design',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,800;1,8..60,400&family=Plus+Jakarta+Sans:wght@500;700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #1B4332; font-family: "Plus Jakarta Sans", sans-serif; color: #F8F5EE;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(circle at 85% 15%, rgba(64, 145, 108, 0.4), transparent 50%), #1B4332;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(248,245,238,0.25);padding-bottom:24px;">
          <span style="font-size:22px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#D8F3DC;">Forestry & Design Series</span>
          <span style="font-size:20px;color:#B7E4C7;background:rgba(216,243,220,0.15);padding:8px 18px;border-radius:20px;">Vol. 03 / 2026</span>
        </div>
        <div style="margin: 40px 0;">
          <div style="display:inline-block;background:#D8F3DC;color:#1B4332;font-size:18px;font-weight:800;padding:6px 16px;border-radius:6px;margin-bottom:24px;">EDITORIAL QUARTERLY</div>
          <h1 style="font-family:'Source Serif 4', serif;font-size:62px;line-height:1.15;font-weight:800;margin:0 0 24px 0;color:#F8F5EE;">Sustainable Forest Infrastructure</h1>
          <p style="font-family:'Source Serif 4', serif;font-size:28px;line-height:1.5;color:#D8F3DC;font-style:italic;margin:0;max-width:850px;">A thoughtful exploration into carbon-neutral materials, regenerative forest management, and enduring timber systems.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#2D6A4F;padding:32px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);">
            <div style="font-size:44px;font-weight:800;color:#95D5B2;margin-bottom:8px;">84%</div>
            <div style="font-size:18px;color:#E9ECEF;font-weight:600;">Carbon Sequestration</div>
          </div>
          <div style="background:#2D6A4F;padding:32px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);">
            <div style="font-size:44px;font-weight:800;color:#D8F3DC;margin-bottom:8px;">12.4k</div>
            <div style="font-size:18px;color:#E9ECEF;font-weight:600;">Hectares Replanted</div>
          </div>
          <div style="background:#2D6A4F;padding:32px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);">
            <div style="font-size:44px;font-weight:800;color:#E8B4B8;margin-bottom:8px;">Zero</div>
            <div style="font-size:18px;color:#E9ECEF;font-weight:600;">Net Waste Lifecycle</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'editorial-tri-tone',
    title: 'Haute Couture Visual Lookbook',
    subtitle: 'Autumn / Winter Modern Editorial Collection',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #4A0E17; font-family: "Plus Jakarta Sans", sans-serif; color: #FDFBF7;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: #4A0E17;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #E5C378;padding-bottom:20px;">
          <span style="font-family:'Bricolage Grotesque', sans-serif;font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#E5C378;">TRI-TONE REVIEW</span>
          <span style="font-size:18px;letter-spacing:1px;color:#E8B4B8;">MILAN / PARIS // 2026</span>
        </div>
        <div style="margin:30px 0;">
          <div style="font-family:'Instrument Serif', serif;font-size:38px;color:#E8B4B8;font-style:italic;margin-bottom:12px;">The Autumn Monograph</div>
          <h1 style="font-family:'Bricolage Grotesque', sans-serif;font-size:68px;line-height:1.05;font-weight:800;margin:0 0 20px 0;color:#FDFBF7;text-transform:uppercase;letter-spacing:-1px;">ARCHITECTURAL DRAPERY & FORM</h1>
          <p style="font-size:22px;line-height:1.5;color:#E5C378;max-width:800px;margin:0;">Dissecting proportion, raw textile weight, and minimalist silhouette construction across modern fashion disciplines.</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1.2fr;gap:30px;">
          <div style="background:#E8B4B8;color:#4A0E17;padding:32px;border-radius:8px;">
            <div style="font-family:'Bricolage Grotesque', sans-serif;font-size:28px;font-weight:800;margin-bottom:8px;">DUSTY PINK</div>
            <div style="font-size:18px;font-weight:600;line-height:1.4;">Tactile softness grounding dramatic architectural contours.</div>
          </div>
          <div style="background:#E5C378;color:#4A0E17;padding:32px;border-radius:8px;">
            <div style="font-family:'Bricolage Grotesque', sans-serif;font-size:28px;font-weight:800;margin-bottom:8px;">MUSTARD ACCENT</div>
            <div style="font-size:18px;font-weight:600;line-height:1.4;">High-contrast focal anchors highlighting key silhouettes.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'grove',
    title: 'Grove Botanical Research',
    subtitle: 'Classical Monographs in Forest Ecology',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #162B1D; font-family: "Plus Jakarta Sans", sans-serif; color: #F5EFE6;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: #162B1D;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(245,239,230,0.3);padding-bottom:24px;">
          <span style="font-family:'Cinzel', serif;font-size:22px;letter-spacing:3px;color:#C17C54;">GROVE CONSERVATORY</span>
          <span style="font-size:18px;color:#D8DEC9;font-style:italic;">EST. 1894 // MONOGRAPH</span>
        </div>
        <div style="margin:40px 0;">
          <div style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:#C17C54;margin-bottom:16px;font-weight:600;">BOTANICAL REPORT</div>
          <h1 style="font-family:'Playfair Display', serif;font-size:62px;line-height:1.15;font-weight:900;margin:0 0 20px 0;color:#F5EFE6;">Old-Growth Forest Canopy Architecture</h1>
          <p style="font-family:'Playfair Display', serif;font-size:26px;line-height:1.5;color:#D8DEC9;font-style:italic;max-width:850px;margin:0;">Measuring microclimate stability, deep mycorrhizal networks, and ancient pine longevity across alpine reserves.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#223E2B;padding:28px;border-radius:6px;border-left:4px solid #C17C54;">
            <div style="font-size:36px;font-family:'Playfair Display', serif;font-weight:900;color:#F5EFE6;margin-bottom:6px;">480+</div>
            <div style="font-size:17px;color:#D8DEC9;">Tree Rings Analyzed</div>
          </div>
          <div style="background:#223E2B;padding:28px;border-radius:6px;border-left:4px solid #D8DEC9;">
            <div style="font-size:36px;font-family:'Playfair Display', serif;font-weight:900;color:#F5EFE6;margin-bottom:6px;">98.2%</div>
            <div style="font-size:17px;color:#D8DEC9;">Canopy Density Index</div>
          </div>
          <div style="background:#223E2B;padding:28px;border-radius:6px;border-left:4px solid #C17C54;">
            <div style="font-size:36px;font-family:'Playfair Display', serif;font-weight:900;color:#F5EFE6;margin-bottom:6px;">14 Bio</div>
            <div style="font-size:17px;color:#D8DEC9;">Symbiotic Flora Pairs</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'long-table',
    title: 'Long Table Supper Club',
    subtitle: 'Seasonal Gastronomy & Wine Pairings',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,700;0,9..144,900;1,9..144,400&family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF7F2; font-family: "Plus Jakarta Sans", sans-serif; color: #2B2118;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#FAF7F2;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #C84B31;padding-bottom:20px;">
          <span style="font-weight:800;font-size:24px;letter-spacing:2px;text-transform:uppercase;color:#C84B31;">LONG TABLE CLUB</span>
          <span style="border:2px solid #C84B31;color:#C84B31;padding:8px 24px;border-radius:40px;font-weight:800;font-size:16px;">AUTUMN TASTING 2026</span>
        </div>
        <div style="margin:40px 0;">
          <div style="font-family:'Fraunces', serif;font-size:32px;font-style:italic;color:#C84B31;margin-bottom:12px;">Farm-to-Table Community Dining</div>
          <h1 style="font-family:'Fraunces', serif;font-size:64px;line-height:1.12;font-weight:900;margin:0 0 24px 0;color:#2B2118;">HEIRLOOM HARVEST & WILD FERMENTATION</h1>
          <p style="font-size:24px;line-height:1.5;color:#635246;max-width:850px;margin:0;">Celebrating small-batch vintners, wood-fired hearth cooking, and shared stories across a twenty-seat timber table.</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
          <div style="background:#F0EAE1;padding:32px;border-radius:16px;border:1px solid #D8CFC4;">
            <div style="font-size:22px;font-weight:800;color:#C84B31;margin-bottom:10px;">COURSE I — HEARTH ROAST</div>
            <div style="font-size:18px;color:#2B2118;line-height:1.4;">Charred autumn squash with smoked goat curd & mountain honey.</div>
          </div>
          <div style="background:#C84B31;color:#FFF;padding:32px;border-radius:16px;">
            <div style="font-size:22px;font-weight:800;margin-bottom:10px;">VINTAGE CELLAR PAIRING</div>
            <div style="font-size:18px;line-height:1.4;color:#FDE8E4;">2019 Natural Skin-Contact Orange Wine, Sonoma Coast.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'mat',
    title: 'Mid-Century Modern Furniture',
    subtitle: 'Organic Woodcraft & Ceramic Studio',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=Lora:ital,wght@0,600;1,400&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #2E3830; font-family: "Plus Jakarta Sans", sans-serif; color: #F4F1EA;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#2E3830;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(244,241,234,0.2);padding-bottom:24px;">
          <span style="font-size:22px;font-weight:800;letter-spacing:3px;color:#E67E22;text-transform:uppercase;">MAT STUDIO DESIGN</span>
          <span style="background:#3C483F;padding:8px 20px;border-radius:6px;font-size:16px;color:#D5CEBF;">COPENHAGEN // 1958</span>
        </div>
        <div style="margin:40px 0;">
          <div style="color:#E67E22;font-size:18px;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">CRAFT & PROPORTION</div>
          <h1 style="font-family:'Lora', serif;font-size:62px;line-height:1.15;font-weight:600;margin:0 0 24px 0;color:#F4F1EA;">Teak, Linen & Sculptural Form</h1>
          <p style="font-size:24px;line-height:1.55;color:#D5CEBF;max-width:850px;margin:0;">Hand-turned solid joinery married with muted sage textiles and warm burnt-orange accents.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#F4F1EA;color:#2E3830;padding:30px;border-radius:8px;">
            <div style="font-size:32px;font-weight:800;color:#E67E22;margin-bottom:6px;">01. Solid Teak</div>
            <div style="font-size:17px;line-height:1.4;font-weight:600;">Sustainably sourced old-growth timber.</div>
          </div>
          <div style="background:#F4F1EA;color:#2E3830;padding:30px;border-radius:8px;">
            <div style="font-size:32px;font-weight:800;color:#2E3830;margin-bottom:6px;">02. Woven Cane</div>
            <div style="font-size:17px;line-height:1.4;font-weight:600;">Hand-knotted natural rush seating.</div>
          </div>
          <div style="background:#F4F1EA;color:#2E3830;padding:30px;border-radius:8px;">
            <div style="font-size:32px;font-weight:800;color:#E67E22;margin-bottom:6px;">03. Raw Brass</div>
            <div style="font-size:17px;line-height:1.4;font-weight:600;">Living patina hardware accents.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'peoples-platform',
    title: 'The People’s Manifesto',
    subtitle: 'Bold Civic Action & Community Power',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Caveat:wght@700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF6ED; font-family: "Plus Jakarta Sans", sans-serif; color: #1D2D44;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:70px;display:flex;flex-direction:column;justify-content:space-between;background:#FAF6ED;border:16px solid #1D2D44;">
        <div style="display:flex;justify-content:space-between;align-items:center;background:#1D2D44;color:#FFF;padding:16px 28px;">
          <span style="font-family:'Alfa Slab One', cursive;font-size:24px;letter-spacing:1px;color:#F4A261;">PEOPLE'S PLATFORM</span>
          <span style="font-family:'Caveat', cursive;font-size:32px;color:#E76F51;">Action Deck 2026!</span>
        </div>
        <div style="margin:30px 0;">
          <div style="background:#E63946;color:#FFF;display:inline-block;padding:8px 20px;font-weight:800;font-size:20px;margin-bottom:20px;transform:rotate(-1deg);">COMMUNITY DEMAND #1</div>
          <h1 style="font-family:'Alfa Slab One', cursive;font-size:64px;line-height:1.08;margin:0 0 20px 0;color:#1D2D44;text-transform:uppercase;">EQUAL HOUSING, CLEAN ENERGY & OPEN PARKS</h1>
          <p style="font-size:26px;line-height:1.45;color:#2B2D42;font-weight:700;max-width:880px;margin:0;">Mobilizing collective neighborhood resources into transparent public investments.</p>
        </div>
        <div style="display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:20px;">
          <div style="background:#E63946;color:#FFF;padding:24px;border:3px solid #1D2D44;box-shadow:6px 6px 0px #1D2D44;">
            <div style="font-family:'Alfa Slab One', cursive;font-size:38px;margin-bottom:4px;">100%</div>
            <div style="font-size:18px;font-weight:800;">Public Accountability</div>
          </div>
          <div style="background:#F4A261;color:#1D2D44;padding:24px;border:3px solid #1D2D44;box-shadow:6px 6px 0px #1D2D44;">
            <div style="font-family:'Alfa Slab One', cursive;font-size:38px;margin-bottom:4px;">50k+</div>
            <div style="font-size:18px;font-weight:800;">Signatures Gathered</div>
          </div>
          <div style="background:#2A9D8F;color:#FFF;padding:24px;border:3px solid #1D2D44;box-shadow:6px 6px 0px #1D2D44;">
            <div style="font-family:'Alfa Slab One', cursive;font-size:38px;margin-bottom:4px;">DAY 1</div>
            <div style="font-size:18px;font-weight:800;">Direct Action Launch</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'pin-and-paper',
    title: 'Qualitative Field Notes',
    subtitle: 'User Interviews & Ethnographic Insights',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Plus+Jakarta+Sans:wght@600;800&family=Space+Mono&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF0D7; font-family: "Plus Jakarta Sans", sans-serif; color: #1E293B;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(circle at 10% 10%, #FFF8E7 0%, #F5E5BE 100%);">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px dashed #B89F70;padding-bottom:20px;">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:32px;">📌</span>
            <span style="font-family:'Space Mono', monospace;font-size:20px;font-weight:700;color:#6B532F;">FIELD_RESEARCH_LOG_04.TXT</span>
          </div>
          <span style="font-family:'Caveat', cursive;font-size:30px;color:#A8422B;transform:rotate(-2deg);">Confidential Debrief</span>
        </div>
        <div style="margin:30px 0;">
          <h1 style="font-family:'Caveat', cursive;font-size:68px;line-height:1.15;font-weight:700;margin:0 0 16px 0;color:#182848;">"The product felt effortless once I discovered the keyboard flow."</h1>
          <p style="font-size:22px;line-height:1.5;color:#4A3F2C;max-width:850px;margin:0;">Synthesizing 42 qualitative user research sessions across design leads, engineers, and product directors.</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
          <div style="background:#FFF9E6;padding:32px;border:1px solid #D6C29E;border-radius:4px;box-shadow:4px 4px 12px rgba(0,0,0,0.06);position:relative;">
            <div style="position:absolute;top:-14px;left:24px;background:#E76F51;color:#FFF;font-size:14px;font-weight:800;padding:4px 12px;border-radius:2px;">KEY THEME #1</div>
            <div style="font-family:'Caveat', cursive;font-size:32px;color:#1E293B;margin-top:8px;line-height:1.3;">Speed beats complexity in high-frequency workflows.</div>
          </div>
          <div style="background:#FFF9E6;padding:32px;border:1px solid #D6C29E;border-radius:4px;box-shadow:4px 4px 12px rgba(0,0,0,0.06);position:relative;">
            <div style="position:absolute;top:-14px;left:24px;background:#2A9D8F;color:#FFF;font-size:14px;font-weight:800;padding:4px 12px;border-radius:2px;">KEY THEME #2</div>
            <div style="font-family:'Caveat', cursive;font-size:32px;color:#1E293B;margin-top:8px;line-height:1.3;">Micro-animations provide immediate confirmation confidence.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'pink-script',
    title: 'After Hours Luxury Soirée',
    subtitle: 'Exclusive Midnight Spirits & Fashion Reveal',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #09090C; font-family: "Plus Jakarta Sans", sans-serif; color: #FFFDF7;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(circle at 80% 20%, rgba(255, 20, 147, 0.25), transparent 60%), #09090C;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,20,147,0.3);padding-bottom:24px;">
          <span style="font-size:22px;font-weight:800;letter-spacing:4px;text-transform:uppercase;color:#FF1493;">AFTER HOURS // MONACO</span>
          <span style="font-family:'Instrument Serif', serif;font-size:28px;font-style:italic;color:#E8B4B8;">Private Client Preview</span>
        </div>
        <div style="margin:40px 0;">
          <div style="font-family:'Instrument Serif', serif;font-size:42px;color:#FF1493;font-style:italic;margin-bottom:12px;">The Nocturne Monograph</div>
          <h1 style="font-family:'Instrument Serif', serif;font-size:72px;line-height:1.08;font-weight:400;margin:0 0 24px 0;color:#FFFDF7;">Sultry Elegance in Velvet & Obsidian</h1>
          <p style="font-size:24px;line-height:1.55;color:#E8B4B8;max-width:850px;margin:0;">A high-voltage midnight gathering celebrating bespoke haute horlogerie and rare vintage champagne.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,20,147,0.3);padding:32px;border-radius:8px;">
            <div style="font-family:'Instrument Serif', serif;font-size:44px;color:#FF1493;margin-bottom:6px;">01. Velvet</div>
            <div style="font-size:16px;color:#CCC;font-weight:500;">Nocturnal tactile finish</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,20,147,0.3);padding:32px;border-radius:8px;">
            <div style="font-family:'Instrument Serif', serif;font-size:44px;color:#FF1493;margin-bottom:6px;">02. Gold</div>
            <div style="font-size:16px;color:#CCC;font-weight:500;">Subtle ambient illumination</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,20,147,0.3);padding:32px;border-radius:8px;">
            <div style="font-family:'Instrument Serif', serif;font-size:44px;color:#FF1493;margin-bottom:6px;">03. Onyx</div>
            <div style="font-size:16px;color:#CCC;font-weight:500;">Absolute black canvas</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'playful',
    title: 'Indie Launchpad 2026',
    subtitle: 'Friendly Creator Tools & Community Drops',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@500;700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FFE8DF; font-family: "Plus Jakarta Sans", sans-serif; color: #3A2518;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(circle at 90% 10%, #FFD6C9 0%, #FFE8DF 100%);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-family:'Syne', sans-serif;font-size:26px;font-weight:800;color:#E05A47;">PLAYFUL.IO</span>
          <span style="background:#FFF;padding:8px 24px;border-radius:40px;font-weight:700;font-size:18px;color:#E05A47;box-shadow:0 4px 12px rgba(224,90,71,0.15);">✨ Version 2.0</span>
        </div>
        <div style="margin:40px 0;">
          <h1 style="font-family:'Syne', sans-serif;font-size:66px;line-height:1.12;font-weight:800;margin:0 0 24px 0;color:#3A2518;">Building Delightful Software for Modern Indie Makers</h1>
          <p style="font-size:26px;line-height:1.5;color:#6C4B38;max-width:850px;margin:0;">No corporate bloat. Just snappy tools, friendly animations, and instant creator superpowers.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#FFF;padding:32px;border-radius:24px;box-shadow:0 8px 24px rgba(224,90,71,0.1);">
            <div style="font-size:40px;margin-bottom:8px;">🚀</div>
            <div style="font-family:'Syne', sans-serif;font-size:24px;font-weight:800;color:#E05A47;margin-bottom:4px;">1-Click Deploy</div>
            <div style="font-size:16px;color:#6C4B38;">Zero devops setup</div>
          </div>
          <div style="background:#FFF;padding:32px;border-radius:24px;box-shadow:0 8px 24px rgba(224,90,71,0.1);">
            <div style="font-size:40px;margin-bottom:8px;">💖</div>
            <div style="font-family:'Syne', sans-serif;font-size:24px;font-weight:800;color:#E05A47;margin-bottom:4px;">Community Loved</div>
            <div style="font-size:16px;color:#6C4B38;">15,000+ indie builders</div>
          </div>
          <div style="background:#FFF;padding:32px;border-radius:24px;box-shadow:0 8px 24px rgba(224,90,71,0.1);">
            <div style="font-size:40px;margin-bottom:8px;">⚡</div>
            <div style="font-family:'Syne', sans-serif;font-size:24px;font-weight:800;color:#E05A47;margin-bottom:4px;">Sub-Second Speed</div>
            <div style="font-size:16px;color:#6C4B38;">Pure static power</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'raw-grid',
    title: 'Raw Neobrutalism Design System',
    subtitle: 'Offset Shadows, Heavy Borders & Unfiltered Energy',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&family=Space+Mono:wght@700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #F4F0EA; font-family: "Plus Jakarta Sans", sans-serif; color: #111;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:70px;display:flex;flex-direction:column;justify-content:space-between;background:#F4F0EA;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:4px solid #111;padding-bottom:20px;">
          <span style="font-family:'Space Mono', monospace;font-size:24px;font-weight:700;background:#FFD166;padding:6px 16px;border:3px solid #111;box-shadow:4px 4px 0 #111;">RAW_GRID.CSS</span>
          <span style="font-weight:800;font-size:18px;border:3px solid #111;padding:6px 16px;box-shadow:4px 4px 0 #111;background:#FFF;">v4.0 BUILD</span>
        </div>
        <div style="margin:30px 0;">
          <h1 style="font-size:64px;line-height:1.05;font-weight:900;margin:0 0 20px 0;color:#111;text-transform:uppercase;">HIGH-CONTRAST NEOBRUTALISM FOR BUILDERS</h1>
          <p style="font-size:24px;line-height:1.45;color:#333;font-weight:700;max-width:850px;margin:0;">No fake gradient blurs. High-density structure, 4px black borders, and hard 6px offset drop shadows.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#FF99C8;padding:28px;border:4px solid #111;box-shadow:6px 6px 0 #111;">
            <div style="font-size:40px;font-weight:900;margin-bottom:4px;">01. SOLID</div>
            <div style="font-size:17px;font-weight:800;">Heavy black hairline bounds</div>
          </div>
          <div style="background:#A9DEF9;padding:28px;border:4px solid #111;box-shadow:6px 6px 0 #111;">
            <div style="font-size:40px;font-weight:900;margin-bottom:4px;">02. PUNCH</div>
            <div style="font-size:17px;font-weight:800;">High-chroma contrast blocks</div>
          </div>
          <div style="background:#E4C1F9;padding:28px;border:4px solid #111;box-shadow:6px 6px 0 #111;">
            <div style="font-size:40px;font-weight:900;margin-bottom:4px;">03. SCRAPPY</div>
            <div style="font-size:17px;font-weight:800;">Direct founder-pitch clarity</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'retro-windows',
    title: 'Windows 95 System Properties',
    subtitle: 'Classic 32-bit Graphical User Interface',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=VT323&family=Plus+Jakarta+Sans:wght@600;700&family=Space+Mono&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #008080; font-family: "MS Sans Serif", Tahoma, sans-serif; color: #000;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:60px;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#008080;">
        <div style="width:960px;background:#C0C0C0;border:3px solid;border-color:#FFF #808080 #808080 #FFF;box-shadow:8px 8px 0 rgba(0,0,0,0.5);padding:6px;">
          <div style="background:#000080;color:#FFF;padding:8px 14px;display:flex;justify-content:space-between;align-items:center;font-weight:bold;font-size:22px;letter-spacing:1px;">
            <span>💾 System Setup — Win95 Presentation Manager</span>
            <div style="display:flex;gap:6px;">
              <span style="background:#C0C0C0;color:#000;padding:2px 8px;border:2px solid;border-color:#FFF #000 #000 #FFF;font-size:16px;">_</span>
              <span style="background:#C0C0C0;color:#000;padding:2px 8px;border:2px solid;border-color:#FFF #000 #000 #FFF;font-size:16px;">X</span>
            </div>
          </div>
          <div style="padding:40px;background:#C0C0C0;">
            <div style="display:flex;gap:30px;align-items:center;margin-bottom:30px;">
              <div style="font-size:72px;">🖥️</div>
              <div>
                <h1 style="font-size:38px;margin:0 0 8px 0;color:#000;">MICROSOFT WINDOWS 95</h1>
                <p style="font-size:20px;color:#333;margin:0;">Authentic 1995 desktop chrome with 3D beveled panels and nostalgic pixel vibes.</p>
              </div>
            </div>
            <div style="background:#FFF;border:2px solid;border-color:#808080 #FFF #FFF #808080;padding:24px;margin-bottom:30px;">
              <div style="font-size:20px;font-weight:bold;margin-bottom:8px;">Computer Specifications:</div>
              <div style="font-size:18px;line-height:1.6;color:#111;">
                • Intel Pentium 133 MHz Processor<br>
                • 32.0 MB High-Performance EDO RAM<br>
                • Sound Blaster 16 & 4X CD-ROM Drive
              </div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:16px;">
              <button style="padding:10px 32px;font-size:18px;font-weight:bold;background:#C0C0C0;border:3px solid;border-color:#FFF #000 #000 #FFF;">OK</button>
              <button style="padding:10px 32px;font-size:18px;font-weight:bold;background:#C0C0C0;border:3px solid;border-color:#FFF #000 #000 #FFF;">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'retro-zine',
    title: 'Riso Press Independent Zine',
    subtitle: 'Hand-Printed Typography & Raw Halftone Ink',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Caveat:wght@700&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #EFE8DA; font-family: "Plus Jakarta Sans", sans-serif; color: #1E3A2F;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#EFE8DA;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #1E3A2F;padding-bottom:20px;">
          <span style="font-family:'Bebas Neue', sans-serif;font-size:36px;letter-spacing:2px;color:#1E3A2F;">UNDERGROUND ZINE NO. 09</span>
          <span style="font-family:'Caveat', cursive;font-size:32px;color:#C84B31;transform:rotate(-3deg);">Limited 200 Copies</span>
        </div>
        <div style="margin:30px 0;">
          <h1 style="font-family:'Bebas Neue', sans-serif;font-size:84px;line-height:0.95;margin:0 0 16px 0;color:#1E3A2F;letter-spacing:1px;">RISO-PRINTED REVOLUTION IN INK</h1>
          <p style="font-size:24px;line-height:1.5;color:#435E54;max-width:850px;margin:0;">Dual-color risograph printing combining soy-based pine green ink with vibrant terracotta halftone stamps.</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
          <div style="background:#1E3A2F;color:#EFE8DA;padding:32px;border-radius:4px;">
            <div style="font-family:'Bebas Neue', sans-serif;font-size:36px;color:#E5A93C;margin-bottom:6px;">SOY INK OVERLAY</div>
            <div style="font-size:18px;line-height:1.4;">Unpredictable organic misregistration giving each print unique soul.</div>
          </div>
          <div style="background:#C84B31;color:#FFF;padding:32px;border-radius:4px;">
            <div style="font-family:'Bebas Neue', sans-serif;font-size:36px;margin-bottom:6px;">DIY CRAFT DISCIPLINE</div>
            <div style="font-size:18px;line-height:1.4;">Hand-bound saddle stitch zines celebrating tactile paper culture.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'sakura-chroma',
    title: '昭和磁带产品手册 / Sakura Chroma',
    subtitle: 'Vintage 80s Japanese Cassette Ribbon Aesthetic',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@800;900&family=Space+Mono:wght@700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF8F5; font-family: "Plus Jakarta Sans", sans-serif; color: #151515;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:70px;display:flex;flex-direction:column;justify-content:space-between;background:#FAF8F5;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;right:0;width:380px;height:100%;background:linear-gradient(135deg, #FF4B4B 0%, #FF8533 25%, #FFD633 50%, #33CC66 75%, #3399FF 100%);opacity:0.85;clip-path:polygon(40% 0, 100% 0, 100% 100%, 0% 100%);"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #151515;padding-bottom:20px;z-index:2;">
          <span style="font-family:'Space Mono', monospace;font-size:24px;font-weight:700;letter-spacing:1px;color:#FF4B4B;">CHROMA-POSITION // TYPE-II</span>
          <span style="font-weight:900;font-size:20px;background:#151515;color:#FFF;padding:6px 18px;">HIGH BIAS 90 MIN</span>
        </div>
        <div style="margin:30px 0;max-width:650px;z-index:2;">
          <div style="font-size:18px;font-weight:900;letter-spacing:3px;text-transform:uppercase;color:#FF4B4B;margin-bottom:12px;">PRECISION ACOUSTIC CASSETTE</div>
          <h1 style="font-size:64px;line-height:1.05;font-weight:900;margin:0 0 20px 0;color:#151515;text-transform:uppercase;">DYNAMIC SOUND REPRODUCTION</h1>
          <p style="font-size:22px;line-height:1.5;color:#444;font-weight:600;margin:0;">Japanese consumer tech packaging inspired by iconic Sony & TDK audio cassettes of the late 1980s.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,200px);gap:20px;z-index:2;">
          <div style="background:#FFF;padding:24px;border:2px solid #151515;box-shadow:4px 4px 0 #151515;">
            <div style="font-size:32px;font-weight:900;color:#FF4B4B;">90 min</div>
            <div style="font-size:15px;font-weight:700;">IEC Type II / CrO2</div>
          </div>
          <div style="background:#FFF;padding:24px;border:2px solid #151515;box-shadow:4px 4px 0 #151515;">
            <div style="font-size:32px;font-weight:900;color:#3399FF;">+4.5 dB</div>
            <div style="font-size:15px;font-weight:700;">High Output Level</div>
          </div>
          <div style="background:#FFF;padding:24px;border:2px solid #151515;box-shadow:4px 4px 0 #151515;">
            <div style="font-size:32px;font-weight:900;color:#33CC66;">0.04%</div>
            <div style="font-size:15px;font-weight:700;">Low Wow & Flutter</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'scatterbrain',
    title: 'Product Design Workshop Sticky Notes',
    subtitle: 'Brainstorm Whiteboard & Divergent Ideation',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Zilla+Slab:wght@700&family=Plus+Jakarta+Sans:wght@600&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF8F2; font-family: "Plus Jakarta Sans", sans-serif; color: #1E293B;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:70px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(#E2DFD2 1.5px, transparent 1.5px) 0 0 / 28px 28px, #FAF8F2;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-family:'Zilla Slab', serif;font-size:28px;font-weight:700;color:#2B3A4A;">🎯 Q3 SPRINT IDEATION BOARD</span>
          <span style="background:#FFE66D;padding:8px 20px;border-radius:4px;font-family:'Caveat', cursive;font-size:28px;color:#111;transform:rotate(2deg);box-shadow:2px 2px 8px rgba(0,0,0,0.1);">Vote with stickers!</span>
        </div>
        <div style="margin:20px 0;">
          <h1 style="font-family:'Zilla Slab', serif;font-size:56px;line-height:1.15;font-weight:700;margin:0 0 12px 0;color:#1E293B;">How might we reduce time-to-first-value by 60%?</h1>
          <p style="font-size:22px;color:#555;margin:0;">Open brainstorming stickies from the cross-functional UX, Engineering & Data teams.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#FF99C8;padding:28px;border-radius:4px;box-shadow:4px 6px 16px rgba(0,0,0,0.08);transform:rotate(-2deg);">
            <div style="font-family:'Caveat', cursive;font-size:32px;color:#111;line-height:1.25;">"Instant demo templates without mandatory signup!"</div>
            <div style="margin-top:16px;font-weight:800;font-size:16px;color:#4A0E2E;">+8 Votes ⭐</div>
          </div>
          <div style="background:#FCF6BD;padding:28px;border-radius:4px;box-shadow:4px 6px 16px rgba(0,0,0,0.08);transform:rotate(1.5deg);">
            <div style="font-family:'Caveat', cursive;font-size:32px;color:#111;line-height:1.25;">"AI assistant auto-fills boilerplate data."</div>
            <div style="margin-top:16px;font-weight:800;font-size:16px;color:#665C00;">+14 Votes ⭐</div>
          </div>
          <div style="background:#D0F4DE;padding:28px;border-radius:4px;box-shadow:4px 6px 16px rgba(0,0,0,0.08);transform:rotate(-1deg);">
            <div style="font-family:'Caveat', cursive;font-size:32px;color:#111;line-height:1.25;">"Real-time visual preview before downloading."</div>
            <div style="margin-top:16px;font-weight:800;font-size:16px;color:#1B4332;">+11 Votes ⭐</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'signal',
    title: 'Global Macroeconomic Report',
    subtitle: 'Institutional Policy Briefing & Executive Summary',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #0B192C; font-family: "Plus Jakarta Sans", sans-serif; color: #F5EFE6;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#0B192C;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #D4AF37;padding-bottom:24px;">
          <span style="font-family:'Cinzel', serif;font-size:24px;letter-spacing:3px;color:#D4AF37;">SIGNAL ADVISORY GROUP</span>
          <span style="font-size:18px;color:#A0B2C6;letter-spacing:1px;">Q4 EXECUTIVE DISCLOSURE</span>
        </div>
        <div style="margin:40px 0;">
          <div style="color:#D4AF37;font-size:18px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">SOVEREIGN DEBT & LIQUIDITY</div>
          <h1 style="font-size:62px;line-height:1.15;font-weight:800;margin:0 0 24px 0;color:#FFFFFF;">Macro Resilience in Volatile Capital Markets</h1>
          <p style="font-size:24px;line-height:1.55;color:#A0B2C6;max-width:850px;margin:0;">A disciplined quantitative assessment of rate cut cycles, sovereign yields, and central bank foreign reserves.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#1E3E62;padding:32px;border-radius:8px;border-top:3px solid #D4AF37;">
            <div style="font-size:42px;font-weight:800;color:#D4AF37;margin-bottom:4px;">$4.2T</div>
            <div style="font-size:17px;color:#E0E8F0;">Cross-Border Capital Flows</div>
          </div>
          <div style="background:#1E3E62;padding:32px;border-radius:8px;border-top:3px solid #D4AF37;">
            <div style="font-size:42px;font-weight:800;color:#D4AF37;margin-bottom:4px;">3.85%</div>
            <div style="font-size:17px;color:#E0E8F0;">10-Year Benchmark Yield</div>
          </div>
          <div style="background:#1E3E62;padding:32px;border-radius:8px;border-top:3px solid #D4AF37;">
            <div style="font-size:42px;font-weight:800;color:#D4AF37;margin-bottom:4px;">AAA</div>
            <div style="font-size:17px;color:#E0E8F0;">Sovereign Credit Rating</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'soft-editorial',
    title: 'The Sunday Monograph',
    subtitle: 'Quiet Essays on Art, Architecture & Solitude',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #FAF8F5; font-family: "Plus Jakarta Sans", sans-serif; color: #2B2D2F;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#FAF8F5;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #D9D2C7;padding-bottom:24px;">
          <span style="font-family:'Cormorant Garamond', serif;font-size:26px;font-style:italic;color:#6B705C;">The Soft Monograph — Issue 12</span>
          <span style="font-size:16px;color:#8F947E;letter-spacing:2px;text-transform:uppercase;">SPRING / SUMMER</span>
        </div>
        <div style="margin:40px 0;">
          <div style="font-size:18px;letter-spacing:3px;text-transform:uppercase;color:#A5A58D;margin-bottom:16px;font-weight:600;">SLOW LIVING ESSAYS</div>
          <h1 style="font-family:'Cormorant Garamond', serif;font-size:68px;line-height:1.12;font-weight:600;margin:0 0 24px 0;color:#2B2D2F;">The Architecture of Natural Morning Light</h1>
          <p style="font-family:'Cormorant Garamond', serif;font-size:28px;line-height:1.5;color:#6B705C;font-style:italic;max-width:850px;margin:0;">Reflections on unadorned plaster walls, linen drapery, and the quiet dignity of uncluttered living spaces.</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
          <div style="background:#F0ECE1;padding:32px;border-radius:4px;">
            <div style="font-family:'Cormorant Garamond', serif;font-size:32px;font-weight:700;color:#2B2D2F;margin-bottom:8px;">Tactile Plaster</div>
            <div style="font-size:18px;color:#6B705C;line-height:1.4;">Unpainted mineral surfaces that age gracefully with sunlight.</div>
          </div>
          <div style="background:#F0ECE1;padding:32px;border-radius:4px;">
            <div style="font-family:'Cormorant Garamond', serif;font-size:32px;font-weight:700;color:#2B2D2F;margin-bottom:8px;">Subtle Linen</div>
            <div style="font-size:18px;color:#6B705C;line-height:1.4;">Diffusing harsh rays into soft ambient luminescence.</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'stencil-tablet',
    title: 'Archaeological Field Records',
    subtitle: 'Earth & Clay Pigments in Ancient Architecture',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&family=Space+Mono:wght@700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #EDE8DF; font-family: "Plus Jakarta Sans", sans-serif; color: #3D352E;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#EDE8DF;border:10px solid #C4A482;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:3px dashed #B08968;padding-bottom:20px;">
          <span style="font-family:'Space Mono', monospace;font-size:22px;font-weight:700;letter-spacing:2px;color:#7F5539;">EXCAVATION_TABLET_VII</span>
          <span style="background:#B08968;color:#FFF;padding:6px 18px;font-size:16px;font-weight:800;">SITE 42 — MESOPOTAMIA</span>
        </div>
        <div style="margin:30px 0;">
          <h1 style="font-size:62px;line-height:1.08;font-weight:900;margin:0 0 20px 0;color:#3D352E;text-transform:uppercase;letter-spacing:1px;">CLAY TABLETS & OCHRE STENCIL PIGMENTS</h1>
          <p style="font-size:24px;line-height:1.45;color:#7F5539;font-weight:700;max-width:850px;margin:0;">Documenting terracotta brick relief inscriptions, volcanic ash mortars, and natural earth mineral dyes.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;">
          <div style="background:#DDB892;color:#3D352E;padding:26px;border:2px solid #7F5539;">
            <div style="font-size:32px;font-weight:900;margin-bottom:4px;">RAW OCHRE</div>
            <div style="font-size:16px;font-weight:700;">Iron oxide mineral wash</div>
          </div>
          <div style="background:#B08968;color:#FFF;padding:26px;border:2px solid #7F5539;">
            <div style="font-size:32px;font-weight:900;margin-bottom:4px;">BURNT CLAY</div>
            <div style="font-size:16px;font-weight:700;">High-fire structural brick</div>
          </div>
          <div style="background:#7F5539;color:#FFF;padding:26px;border:2px solid #3D352E;">
            <div style="font-size:32px;font-weight:900;margin-bottom:4px;">VOLCANIC</div>
            <div style="font-size:16px;font-weight:700;">Hydraulic ash binder</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'studio',
    title: 'STUDIO ELECTRIC YELLOW',
    subtitle: 'High-Voltage Creative Agency Credentials',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #0A0A0A; font-family: "Plus Jakarta Sans", sans-serif; color: #FFFFFF;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background:#0A0A0A;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #FAFF00;padding-bottom:20px;">
          <span style="font-family:'Archivo Black', sans-serif;font-size:26px;letter-spacing:2px;color:#FAFF00;">STUDIO / VOLTAGE</span>
          <span style="background:#FAFF00;color:#000;font-weight:900;font-size:18px;padding:6px 18px;">AGENCY CREDENTIALS 2026</span>
        </div>
        <div style="margin:40px 0;">
          <h1 style="font-family:'Archivo Black', sans-serif;font-size:68px;line-height:1.05;margin:0 0 24px 0;color:#FFFFFF;text-transform:uppercase;">RADICAL CREATIVE DIRECTION & BRAND ARCHITECTURE</h1>
          <p style="font-size:26px;line-height:1.45;color:#FAFF00;font-weight:700;max-width:850px;margin:0;">High-contrast visual systems built for boundary-pushing founders, global music icons, and culture-shaping brands.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:#1A1A1A;border:2px solid #FAFF00;padding:32px;">
            <div style="font-family:'Archivo Black', sans-serif;font-size:44px;color:#FAFF00;margin-bottom:6px;">48+</div>
            <div style="font-size:18px;font-weight:700;color:#FFF;">Global Design Awards</div>
          </div>
          <div style="background:#1A1A1A;border:2px solid #FAFF00;padding:32px;">
            <div style="font-family:'Archivo Black', sans-serif;font-size:44px;color:#FAFF00;margin-bottom:6px;">$2.4B</div>
            <div style="font-size:18px;font-weight:700;color:#FFF;">Client Value Created</div>
          </div>
          <div style="background:#FAFF00;padding:32px;color:#000;">
            <div style="font-family:'Archivo Black', sans-serif;font-size:44px;margin-bottom:6px;">ZERO</div>
            <div style="font-size:18px;font-weight:900;">Boring Compromises</div>
          </div>
        </div>
      </div>
    `
  },
  {
    slug: 'vellum',
    title: 'Scholarly Treatise on Mathematics',
    subtitle: 'Geometric Rigor & Mathematical Philosophy',
    fontLinks: '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@500;700&display=swap" rel="stylesheet">',
    bodyStyle: 'background: #0B132B; font-family: "Plus Jakarta Sans", sans-serif; color: #FAF0CA;',
    html: `
      <div style="width:100%;height:100%;box-sizing:border-box;padding:80px;display:flex;flex-direction:column;justify-content:space-between;background: radial-gradient(circle at 80% 20%, rgba(28, 77, 107, 0.4), transparent 60%), #0B132B;">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(250,240,202,0.25);padding-bottom:24px;">
          <span style="font-family:'Cormorant Garamond', serif;font-size:26px;font-style:italic;color:#48CAE4;">Vellum Scholarly Monographs</span>
          <span style="font-size:16px;letter-spacing:3px;color:#FAF0CA;text-transform:uppercase;">VOLUME XIV // OXFORD</span>
        </div>
        <div style="margin:40px 0;">
          <div style="font-size:18px;letter-spacing:2px;text-transform:uppercase;color:#48CAE4;margin-bottom:16px;font-weight:600;">THEORETICAL PHYSICS & TOPOLOGY</div>
          <h1 style="font-family:'Cormorant Garamond', serif;font-size:68px;line-height:1.12;font-weight:600;margin:0 0 24px 0;color:#FAF0CA;">Topological Invariants in High-Dimensional Manifolds</h1>
          <p style="font-family:'Cormorant Garamond', serif;font-size:28px;line-height:1.5;color:#48CAE4;font-style:italic;max-width:850px;margin:0;">A quiet, rigorous investigation into differential forms, Poincaré duality, and algebraic invariants.</p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
          <div style="background:rgba(28,77,107,0.3);border:1px solid rgba(72,202,228,0.3);padding:32px;border-radius:6px;">
            <div style="font-family:'Cormorant Garamond', serif;font-size:42px;font-weight:700;color:#FAF0CA;margin-bottom:4px;">Hⁿ(M, ℝ)</div>
            <div style="font-size:16px;color:#48CAE4;">De Rham Cohomology</div>
          </div>
          <div style="background:rgba(28,77,107,0.3);border:1px solid rgba(72,202,228,0.3);padding:32px;border-radius:6px;">
            <div style="font-family:'Cormorant Garamond', serif;font-size:42px;font-weight:700;color:#FAF0CA;margin-bottom:4px;">χ(M) = 2</div>
            <div style="font-size:16px;color:#48CAE4;">Euler Characteristic</div>
          </div>
          <div style="background:rgba(28,77,107,0.3);border:1px solid rgba(72,202,228,0.3);padding:32px;border-radius:6px;">
            <div style="font-family:'Cormorant Garamond', serif;font-size:42px;font-weight:700;color:#FAF0CA;margin-bottom:4px;">π₁(X) ≅ ℤ</div>
            <div style="font-size:16px;color:#48CAE4;">Fundamental Group</div>
          </div>
        </div>
      </div>
    `
  }
];

async function generateAll() {
  const tmpHtml = '/tmp/preview_render.html';
  for (const t of templates) {
    const fullHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        ${t.fontLinks}
        <style>
          * { box-sizing: border-box; }
          body, html { margin: 0; padding: 0; width: 1080px; height: 1080px; overflow: hidden; -webkit-font-smoothing: antialiased; }
        </style>
      </head>
      <body style="${t.bodyStyle}">
        ${t.html}
      </body>
      </html>
    `;
    fs.writeFileSync(tmpHtml, fullHtml, 'utf8');
    const outPng = path.join(outputDir, `${t.slug}.png`);
    const cmd = `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --screenshot="${outPng}" --window-size=1080,1080 --virtual-time-budget=2000 "file://${tmpHtml}"`;
    try {
      execSync(cmd, { stdio: 'pipe' });
      console.log(`✓ Generated ${t.slug}.png`);
    } catch (e) {
      console.error(`✗ Error generating ${t.slug}:`, e.message);
    }
  }
}

generateAll();

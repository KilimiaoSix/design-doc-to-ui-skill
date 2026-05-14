# Cross-Endpoint APP Style Catalog

This catalog contains 20 approved APP visual styles. Each style has:

- A generated four-endpoint style board covering Web, PC, Mobile, and Tablet.
- A style definition in `styles/<id>-<slug>/style.md`.
- A final image-generation prompt in `styles/<id>-<slug>/prompt.txt`.
- A review file in `styles/<id>-<slug>/review.md`.

Use this catalog as a Style Gate asset before generating full APP UI screens from product documents.

## How To Use

1. Read the product/design document and summarize product domain, users, core workflows, and visual constraints.
2. Pick 2-3 candidate styles from this catalog that fit the domain.
3. Show the user style names, tradeoffs, and sample boards when style is ambiguous.
4. Lock the selected style into a `global_style_contract`.
5. Use the selected style's `prompt.txt` as the seed for page-level image prompts.
6. Evaluate generated pages against the selected style's review risks and endpoint rules.

## Endpoint Definition

- Web: browser app or responsive web experience.
- PC: desktop app or desktop-width productivity interface.
- Mobile: native phone app or mobile-first product.
- Tablet: expanded touch interface with split panes, wider cards, or multi-column layouts.

## Approved Styles

| ID | Style | Best For | Web Cue | PC Cue | Mobile Cue | Tablet Cue | Sample |
|---:|---|---|---|---|---|---|---|
| 01 | iOS Liquid Glass Native | Native-first consumer apps, calm dashboards | translucent dashboard | macOS-like app frame | stacked native cards | split glass panels | `generated-samples/01-ios-liquid-glass-native-style-board.png` |
| 02 | Material 3 Expressive | Android-first utility and lifestyle apps | dynamic color cards | expressive responsive shell | large rounded controls | adaptive two-column cards | `generated-samples/02-material-3-expressive-style-board.png` |
| 03 | Fluent Productivity | Enterprise productivity and work hubs | light work dashboard | Windows-like command surface | compact work list | productivity split view | `generated-samples/03-fluent-productivity-style-board.png` |
| 04 | Minimal Clean SaaS | B2B SaaS, analytics, operations | clean KPI dashboard | dense table and chart workspace | simplified KPI list | wider analytics cards | `generated-samples/04-minimal-clean-saas-style-board.png` |
| 05 | Dark Pro Tool | Creator, developer, data, and expert tools | dark workspace | dense panels and canvas | compact pro controls | expanded inspector layout | `generated-samples/05-dark-pro-tool-style-board.png` |
| 06 | Glassmorphism Premium | Premium dashboards, finance-lite, portals | layered glass dashboard | dark frosted analytics | glass card stack | translucent split layout | `generated-samples/06-glassmorphism-premium-style-board.png` |
| 07 | Neumorphism Soft UI | Sparse wellness, habit, IoT controls | soft raised dashboard | tactile control panel | large soft controls | spacious control cards | `generated-samples/07-neumorphism-soft-ui-style-board.png` |
| 08 | Bento Dashboard | Metrics, status boards, AI/work ops | modular card grid | mixed dashboard modules | stacked summary cards | asymmetric bento grid | `generated-samples/08-bento-dashboard-style-board.png` |
| 09 | Neo-Brutalist Bold | Youth brands, experiments, memorable tools | high-contrast board | bold desktop command UI | chunky controls | loud modular layout | `generated-samples/09-neo-brutalist-bold-style-board.png` |
| 10 | Claymorphism Playful 3D | Kids, habit, reward, onboarding | playful card dashboard | 3D learning workspace | friendly task tracker | planner with rewards | `generated-samples/10-claymorphism-playful-3d-style-board.png` |
| 11 | Skeuomorphic Realistic | Audio, craft, nostalgia, finance collectibles | realistic panel app | hardware-like desktop console | physical controls | material-rich tablet UI | `generated-samples/11-skeuomorphic-realistic-style-board.png` |
| 12 | Editorial Magazine | Content, travel, lifestyle, brand storytelling | image-led story grid | editorial reading workspace | article stream | magazine-style split view | `generated-samples/12-editorial-magazine-style-board.png` |
| 13 | Luxury Premium | Premium services, travel, fashion, membership | elegant discovery portal | dark refined desktop | premium booking flow | immersive product cards | `generated-samples/13-luxury-premium-style-board.png` |
| 14 | Fintech Trust | Banking, investment, insurance, wallets | trustworthy finance dashboard | portfolio workstation | account summary cards | expanded charts and alerts | `generated-samples/14-fintech-trust-style-board.png` |
| 15 | Health Calm | Healthcare, wellness, therapy, habit health | calm care dashboard | appointment and record workspace | reassuring daily care | split patient/wellness view | `generated-samples/15-health-calm-style-board.png` |
| 16 | Education Playful | Learning, kids, tutoring, skill apps | course progress hub | learning workspace | lesson path and rewards | classroom activity board | `generated-samples/16-education-playful-style-board.png` |
| 17 | Commerce Retail | Shopping, catalog, marketplace, checkout | product grid and offers | retail management/catalog | product detail and cart | browsing plus checkout | `generated-samples/17-commerce-retail-style-board.png` |
| 18 | Social Content Feed | Communities, creators, media feeds | content stream and side rail | creator desktop feed | mobile feed-first UI | media grid and conversation | `generated-samples/18-social-content-feed-style-board.png` |
| 19 | AI Assistant Copilot | AI tools, productivity copilots, research | chat plus artifacts | copilot workspace | prompt composer | context and output panes | `generated-samples/19-ai-assistant-copilot-style-board.png` |
| 20 | Gamified Growth | Growth loops, missions, events, loyalty | mission dashboard | leaderboard and ops panel | quests and rewards | event map and progress | `generated-samples/20-gamified-growth-style-board.png` |

## Main Review Result

- Style count: 20.
- Generated sample count: 20.
- Review status: all `approved`.
- Each approved sample includes Web, PC, Mobile, and Tablet examples.
- Contact sheet: `style-board-contact-sheet.png`.

## Source Anchors

See `sources/research-notes.md` for source links and extracted constraints.

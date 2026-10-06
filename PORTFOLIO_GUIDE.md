# Latchya.R — Personal Portfolio Website Guide

Welcome to your personal portfolio website! This portfolio is specifically tailored for a 2nd-year B.Tech Artificial Intelligence & Machine Learning student at R.M.D. Engineering College.

---

## 📁 Project Files

| File | Description |
| :--- | :--- |
| **`index.html`** | The main website structure with all 7 sections (Home, About, Education, Skills, Projects, Certifications, Contact) and the interactive modals. |
| **`style.css`** | The complete design system with minimal lavender & crisp white palette, smooth responsive breakpoints, and animations. |
| **`script.js`** | Interactive AI canvas particle animation, sticky navigation, mobile drawer menu, contact form feedback, and the high-resolution certificate lightbox viewer. |
| **`assets/`** | Contains your profile photo (`latchya-photo.png`) and the high-resolution certificate images (`cert-nptel.png`, `cert-oracle-agentic-ai.png`, `cert-adobe-hackathon.png`, `cert-international-conference.png`). |

---

## 🚀 How to View Your Website

### Instant Local Preview
1. Simply double-click **`index.html`** in your folder, or
2. Run this command in PowerShell from the project folder:
   ```powershell
   Invoke-Item index.html
   ```
Your default browser (Chrome, Edge, Firefox) will immediately open the website.

---

## 🌐 How to Publish for Free on GitHub Pages

Since all code is written in clean, modern HTML, CSS, and JavaScript with zero build steps, you can host it live on the web in 3 simple steps:

1. **Create a GitHub Repository**:
   - Go to [github.com/new](https://github.com/new).
   - Name it either:
     - `Latchya-R.github.io` (for a root personal domain), or
     - `portfolio` (for `https://latchya-r.github.io/portfolio`).
2. **Push these files**:
   ```bash
   git init
   git add index.html style.css script.js assets/
   git commit -m "Launch Latchya.R personal portfolio"
   git branch -M main
   git remote add origin https://github.com/Latchya-R/<repo-name>.git
   git push -u origin main
   ```
3. **Turn on GitHub Pages**:
   - In your GitHub repo, go to **Settings > Pages**.
   - Under **Branch**, select `main` and `/ (root)`, then click **Save**.
   - Your live website will be up and running within 60 seconds!

---

## 🎨 Summary of Features
- **Aesthetic**: Minimal lavender and white with subtle AI network background constellation.
- **Hero**: Your portrait photo with rotating lavender dashed ring and sparkle badge.
- **Education**: Visual badges highlighting your CGPA **9.05** (B.Tech), **90.5%** (12th HSC), and **88.4%** (10th SSLC).
- **Projects**: Clean, concise student cards for Legal Metrology Label Inspection, MEDISYNC AI (Concept), Crowd Disaster Prevention System, and Smart Biodegradable Packaging.
- **Certifications**: Live interactive preview & lightbox modal for your NPTEL, Oracle, Adobe Hackathon, and International Conference certificates.
- **Contact**: Direct links for `latchya.r07@gmail.com`, your GitHub profile, LinkedIn placeholder, and an interactive message form.

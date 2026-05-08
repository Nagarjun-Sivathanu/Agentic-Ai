with open("static/script.js", "r", encoding="utf-8") as f:
    content = f.read()

# Injection for IMAGE_DISPLAY
old_snippet = """        // Handle Map Embeds separately
        if (trimmed.startsWith(\'MAP_EMBED:\')) {
            const url = trimmed.replace(\'MAP_EMBED:\', \'\').trim();
            mapHTML += `<div class="map-container"><iframe src="${url}"></iframe></div>`;
            return false;
        }"""

new_snippet = """        // Handle Map Embeds separately
        if (trimmed.startsWith(\'MAP_EMBED:\')) {
            const url = trimmed.replace(\'MAP_EMBED:\', \'\').trim();
            mapHTML += `<div class="map-container"><iframe src="${url}"></iframe></div>`;
            return false;
        }
        
        // Handle Image Displays
        if (trimmed.startsWith(\'IMAGE_DISPLAY:\')) {
            const url = trimmed.replace(\'IMAGE_DISPLAY:\', \'\').trim();
            mapHTML += `
                <div class="visual-container">
                    <div class="image-card" onclick="window.open(\'${url}\', \'_blank\')">
                        <img src="${url}" loading="lazy" alt="Visual Insight" 
                             onload="this.parentElement.style.background=\'none\'">
                        <div class="image-overlay">Click to view high-res</div>
                    </div>
                </div>
            `;
            return false;
        }"""

content = content.replace(old_snippet, new_snippet)

with open("static/script.js", "w", encoding="utf-8") as f:
    f.write(content)

import re

with open("static/script.js", "r", encoding="utf-8") as f:
    content = f.read()

# I will replace the formatMarkdown function with a hardened version.
# Using a simpler string replacement to avoid re.sub escape issues.

new_function = r"""
// --- RICH MARKDOWN RENDERER ---
function formatMarkdown(text) {
    if (!text) return "";
    
    // A. Protocols (Global search & extract)
    let visualsHTML = "";
    
    // 1. Map Embeds
    const mapRegex = /MAP_EMBED:(https?:\/\/[^\s\n\r]+)/gi;
    text = text.replace(mapRegex, (match, url) => {
        visualsHTML += `<div class="map-container"><iframe src="${url}"></iframe></div>`;
        return "";
    });
    
    // 2. Image Displays
    const imgRegex = /IMAGE_DISPLAY:(https?:\/\/[^\s\n\r]+)/gi;
    text = text.replace(imgRegex, (match, url) => {
        visualsHTML += `
            <div class="visual-container">
                <div class="image-card" onclick="window.open('${url}', '_blank')">
                    <img src="${url}" loading="lazy" alt="Visual Insight">
                    <div class="image-overlay">Click to view high-res</div>
                </div>
            </div>`;
        return "";
    });

    // 3. Filter internal protocol triggers
    text = text.replace(/TOOL_REQUEST:[^\n]*/gi, "");

    // B. Markdown Core (Simple)
    let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Tables
    const tableRegex = /\|(.+)\|.*\n\|([-| :]+)\|.*\n((\|.*\|.*\n)*)/g;
    html = html.replace(tableRegex, (match, header, divider, rows) => {
        const headers = header.split('|').filter(h => h.trim()).map(h => `<th>${h.trim()}</th>`).join('');
        const rowHTML = rows.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        return `<div style="overflow-x:auto;"><table><thead><tr>${headers}</tr></thead><tbody>${rowHTML}<tbody></table></div>`;
    });

    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\[\[(.*?)\]\]/g, (match, term) => {
        return `<span class="insight-link" onclick="openInsight('${term.replace(/'/g, "\\'").replace(/"/g, '\\"')}')">${term}</span>`;
    });
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/\n/g, '<br>');

    return visualsHTML + html;
}
"""

start_marker = "// --- RICH MARKDOWN RENDERER ---"
end_marker = "return mapHTML + html;\n}"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_function.strip() + "\n" + content[end_idx:]
    with open("static/script.js", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Patch Applied")
else:
    print(f"Markers not found: start={start_idx}, end={end_idx}")
    exit(1)

with open("static/style.css", "a", encoding="utf-8") as f:
    f.write("""
/* Image Gallery & Visuals */
.visual-container {
    margin: 15px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: flex-start;
}
.image-card {
    position: relative;
    width: 100%;
    max-width: 480px;
    height: 320px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    border: 1px solid rgba(0,0,0,0.05);
    background: #f1f3f4;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.2), box-shadow 0.3s ease;
    cursor: zoom-in;
}
.image-card:hover {
    transform: scale(1.03) translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}
.image-card img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    transition: filter 0.4s ease;
}
.image-card:hover img {
    filter: brightness(1.05) contrast(1.05);
}
.image-card .image-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 20px;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    color: white;
    font-size: 0.85rem;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}
.image-card:hover .image-overlay { opacity: 1; }
.skeleton-container {
    width: 100%; max-width: 480px; height: 320px;
    border-radius: 20px;
    background: linear-gradient(90deg, #f1f3f4 25%, #e8eaed 50%, #f1f3f4 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
@media (max-width: 768px) {
    .chat-container { padding: 40px 5%; }
    .image-card { height: 240px; }
}
""")

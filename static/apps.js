// Lógica del formulario de notas.
// Está en un archivo externo (no inline) para cumplir con la Content
// Security Policy estricta definida por Flask-Talisman: default-src 'self'.
document.getElementById('noteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;
    const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content })
    });
    if (res.ok) {
        location.reload();
    } else {
        alert('Error al guardar la nota');
    }
});

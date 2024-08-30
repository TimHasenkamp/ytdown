document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('download-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Verhindert das Standard-Formular-Absenden

        // Zeige den Loader an
        loadingOverlay.style.display = 'flex';

        // Bereite die Daten für den Backend-Call vor
        const formData = new FormData(form);

        // Führe den Backend-Call durch
        fetch('/download', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // Prüfe, ob die Antwort erfolgreich ist
            if (response.ok) {
                return response.blob(); // Wir erwarten eine Datei
            } else {
                throw new Error('Download fehlgeschlagen.');
            }
        })
        .then(blob => {
            // Erstelle einen temporären Download-Link und klicke darauf, um den Download zu starten
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = ''; // Hier kannst du optional den Dateinamen setzen
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);
        })
        .catch(error => {
            console.error(error);
            alert('Ein Fehler ist beim Download aufgetreten.');
        })
        .finally(() => {
            // Blende den Loader aus, sobald der Download abgeschlossen oder ein Fehler aufgetreten ist
            loadingOverlay.style.display = 'none';
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const legalAccordion = document.getElementById('legalAccordion');
    const impressumButton = document.querySelector('button[data-target="#collapseImpressum"]');
    const haftungsausschlussButton = document.querySelector('button[data-target="#collapseHaftungsausschluss"]');
    const impressumCollapse = document.getElementById('collapseImpressum');
    const haftungsausschlussCollapse = document.getElementById('collapseHaftungsausschluss');

    function checkAccordionVisibility() {
        // Wenn keiner der Tabs geöffnet ist, setze das Display auf none
        if (!impressumCollapse.classList.contains('show') && !haftungsausschlussCollapse.classList.contains('show')) {
            legalAccordion.style.display = 'none';
        }
    }

    // Beim Klick auf einen der Buttons das Accordion anzeigen
    impressumButton.addEventListener('click', function() {
        legalAccordion.style.display = 'block';
    });

    haftungsausschlussButton.addEventListener('click', function() {
        legalAccordion.style.display = 'block';
    });

    // Überwache das Schließen der einzelnen Collapse-Elemente
    impressumCollapse.addEventListener('hidden.bs.collapse', checkAccordionVisibility);
    haftungsausschlussCollapse.addEventListener('hidden.bs.collapse', checkAccordionVisibility);

    // Beim Öffnen eines Collapse-Elements sicherstellen, dass das Accordion angezeigt wird
    impressumCollapse.addEventListener('show.bs.collapse', function() {
        legalAccordion.style.display = 'block';
    });

    haftungsausschlussCollapse.addEventListener('show.bs.collapse', function() {
        legalAccordion.style.display = 'block';
    });
});

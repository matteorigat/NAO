function sendFeedback() {
    const selectedEmoji = document.querySelector('input[name="emotion"]:checked');
    const selectedSAM = document.querySelector('input[name="sam-valence"]:checked');
    const selectedSAM2 = document.querySelector('input[name="sam-arousal"]:checked');

    if (!selectedEmoji) {
        alert('Seleziona un\'emoji!');
        return;
    }
    if (!selectedSAM) {
        alert('Seleziona un valore per il primo SAM!');
        return;
    }
    if (!selectedSAM2) {
        alert('Seleziona un valore per il secondo SAM!');
        return;
    }

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emotion: selectedEmoji.value, valence: selectedSAM.value, arousal: selectedSAM2.value })
    })
    .then(response => {
    if (response.status === 303) {
        const redirectUrl = "/"
        if (redirectUrl) {
            // Se esiste l'intestazione Location, fai il redirect
            window.location.href = redirectUrl;
        } else {
            console.error('Redirect URL non trovato nel response header');
        }
    } else if (response.status === 308) {
        const redirectUrl = "/thanks"
        if (redirectUrl) {
            window.location.href = redirectUrl;
        } else {
            console.error('Redirect URL non trovato nel response header');
        }
    } else if (response.ok) {  // Se la risposta è 200-299, la richiesta è andata a buon fine
        return response.json();
    } else {
        throw new Error('Errore nella risposta dal server');
    }
})
.then(data => {
    // Questo viene eseguito solo se la risposta è OK (codice di stato 200)
    console.log(data);  // Puoi anche gestire i dati del server qui
    resetPage();  // La funzione per resettare la pagina, o altre azioni
})
.catch(error => {
    console.error('Errore:', error);
});
}


function repeatGesture() {
    fetch('/repeat', { method: 'POST' })
    .then(response => response.json())
    .then(console.log)
    .catch(console.error);
}


function resetPage() {
    // Deseleziona tutte le opzioni radio per emoji
    const emojiRadios = document.querySelectorAll('input[name="emotion"]');
    emojiRadios.forEach(radio => radio.checked = false);

    // Deseleziona tutte le opzioni radio per il primo SAM
    const samRadios = document.querySelectorAll('input[name="sam-valence"]');
    samRadios.forEach(radio => radio.checked = false);

    // Deseleziona tutte le opzioni radio per il secondo SAM
    const sam2Radios = document.querySelectorAll('input[name="sam-arousal"]');
    sam2Radios.forEach(radio => radio.checked = false);
}
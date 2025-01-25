document.getElementById('questionario-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Blocca l'invio predefinito del modulo

    let allValid = true; // Flag per verificare se tutte le domande sono valide
    const questions = document.querySelectorAll('.question-container');

    questions.forEach((container) => {
        // Rimuovi temporaneamente la classe per riavviare l'animazione
        container.classList.remove('unanswered');

        const radios = container.querySelectorAll('input[type="radio"]');
        const isAnswered = Array.from(radios).some((radio) => radio.checked);

        if (!isAnswered) {
            allValid = false; // Segnala che ci sono errori
            // Utilizza un timeout per consentire il riapplicare della classe
            setTimeout(() => {
                container.classList.add('unanswered');
            }, 10); // Tempo minimo per riattivare l'animazione
        }
    });

    if (allValid) {
        // Se tutte le domande sono valide, invia il modulo
        this.submit();
    } else {
        // Scorri fino alla prima domanda non valida
        const firstInvalid = document.querySelector('.unanswered');
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
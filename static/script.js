// Fonction pour envoyer une remarque opérateur
async function envoyerRemarque() {
    const com = document.getElementById('commentaire').value;
    const response = await fetch('/api/remarque_op', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({commentaire: com})
    });
    if(response.ok) {
        document.getElementById('msg-success').style.display = 'block';
        document.getElementById('commentaire').value = '';
    }
}

// Fonction pour envoyer une intervention référent
async function envoyerIntervention() {
    const data = {
        ligne: document.getElementById('ligne').value,
        machine: document.getElementById('machine').value,
        nom_op: document.getElementById('nom_op').value,
        description: document.getElementById('desc').value,
        id_referent: localStorage.getItem('user_id') // Stocké lors du login
    };

    const response = await fetch('/api/save_intervention', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    if(response.ok) alert("Intervention enregistrée !");
}

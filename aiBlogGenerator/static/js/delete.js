const deleteButtons = document.querySelectorAll( ".delete" );
deleteButtons.forEach((button)=>{
    const id = button.id.slice(7);
    button.addEventListener('click', async function(event){
        try {
            const response = await fetch('/delete/'+ id +'/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id })
            });


        } catch (error) {
            console.error("Error occurred:", error);
            alert("Failed deletion of blog post. Please try again later.");
            
        }
    });
});


document.getElementById('delete-all').addEventListener('click', async function(event){
    try {
        const response = await fetch('/delete-all/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });


    } catch (error) {
        console.error("Error occurred:", error);
        alert("Failed deletion. Please try again later.");
        
    }
});
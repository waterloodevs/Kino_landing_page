function submit_email(){

    var new_email = document.getElementById('email_field').value;

    database.ref().child("email_addresses").push().set({
    email: new_email
    });
    database.goOffline();
}
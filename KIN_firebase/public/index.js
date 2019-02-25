function submit_email(id){
    var new_email = document.getElementById(id).value;
    database.ref().child("email_addresses").push().set({
    email: new_email
    });
    database.goOffline();
    function validate() {
    setTimeout(function() {
      $( ".buttonCTA" ).addClass( "validate", 450, callback );
      $( ".buttonCTA" ).removeClass( "onclic" );
    }, 2250 );
    }
    function callback() {
      setTimeout(function() {
        $( ".buttonCTA" ).removeClass( "validate" );
      }, 1250 );
    }
    $( ".buttonCTA" ).addClass( "onclic", 250, validate);
   return false;
}


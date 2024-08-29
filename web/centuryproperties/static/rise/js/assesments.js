var student_name = sessionStorage.getItem("student_name");
var student_number = sessionStorage.getItem("student_number");
var gender = sessionStorage.getItem("gender");
var student_class = sessionStorage.getItem("student_class");
var token = sessionStorage.getItem("token");

$(document).ready(function(){


    $('#report_button').click(function(){

        $('#token_modal').modal('show');




     });

     var tokenArray = ['12345', '67890', '54321', '09876', '13579'];
     $('#token_submit').click(function(){

            var access_token = $("#access_token").val();

            var tokenExists = tokenArray.includes(access_token);
       // Display result based on token existence
       if (tokenExists) {

        $('#token_modal').modal('hide');
        $('#report_modal').modal('show');

    } else {
        alert('Token does not exist in the array.');
    }

     });






///// Static bar   ///
$(".profile_picture").attr('src','https://riseandshinehighschoolntinda.com/Photos/passport_photos/'+student_number+'.png');
$(".student_number").html(student_number);
$(".student_name").html(student_name);

});
//////////////////// A-LEVEL ///////////////

if(student_class=="S5" || student_class=="S6"){

    $('#report_iframe').attr('src', 'https://riseandshinehighschoolntinda.com/studentsportal/reports/al_mt_report_veiwer.html');



    $.ajax({
        url: 'https://www.riseandshinehighschoolntinda.com/post/students_portal/assesments.php?student_number='+student_number+'&student_class='+student_class+'',
        async : false,  //Enables results in gloaba variable
     }).done(function(response){
        result = JSON.parse(response);
        console.log(result);

        //result = response
    }).fail(function(error){
        console.log(error)
    })


       var results_table = $('#results_table').DataTable({
            columns: [
                { title: 'SUBJECT'},
                { title: 'MT_P1'},
                { title: 'EOT_P1'},
                { title: 'MT_P2'},
                { title: 'EOT_P2'},
                { title: 'MT_P3'},
                { title: 'EOT_P3'},
                { title: 'MT_P4'},
                { title: 'EOT_P4'},
                { title: 'MT_P5'},
                { title: 'EOT_P5'},
                { title: 'MT_P6'},
                { title: 'EOT_P6'}

            ],
            data: result
        });
}

//////////////////// O-LEVEL ///////////////
else{

    $('#report_iframe').attr('src', 'https://riseandshinehighschoolntinda.com/studentsportal/reports/single_activity_report_veiwer.html');
    console.log(student_class);
    $.ajax({
    url: 'https://www.riseandshinehighschoolntinda.com/post/students_portal/assesments.php?student_number='+student_number+'&student_class='+student_class+'',
    async : false,  //Enables results in gloaba variable
 }).done(function(response){
    result = JSON.parse(response);
    console.log(result);

    //result = response
}).fail(function(error){
    console.log(error)
})

   var results_table = $('#results_table').DataTable({
        columns: [
            { title: 'SUBJECT'},
            { title: 'ACTIVITY-1'},
            { title: 'ACTIVITY-2'},
            { title: 'ACTIVITY-3'},
            { title: 'EXAM-1'},
            { title: 'EXAM-2'},
            { title: 'COMMENT'}
        ],
        data: result
    });}





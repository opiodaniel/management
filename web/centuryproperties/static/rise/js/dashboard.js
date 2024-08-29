

 var student_name = sessionStorage.getItem("student_name");
 var student_number = sessionStorage.getItem("student_number");
 var gender = sessionStorage.getItem("gender");
 var student_class = sessionStorage.getItem("student_class");
 var token = sessionStorage.getItem("token");


 $(document).ready(function(){
///// Static bar   ///
 $(".profile_picture").attr('src','https://riseandshinehighschoolntinda.com/Photos/passport_photos/'+student_number+'.jpg');
 $(".student_number").html(student_number);
 $(".student_name").html(student_name);

 });

  $.ajax({
    url: 'https://riseandshinehighschoolntinda.com/post/admin/student_payment_data.php?student_number='+student_number+'',
    async : false,  //Enables results in gloaba variable
 }).done(function(response){
    result = JSON.parse(response)
//console.log(student_number)

}).fail(function(error){
    console.log(error)
});

var   student_number = result[0].student_number;
var   student_name = result[0].student_name;
var   student_class = result[0].student_class;
var   gender = result[0].gender;
var   dob = result[0].dob;
var   program = result[0].program;
var    nationality = result[0].nationality;
var    student_address = result[0].student_address;
var    parent_name = result[0].parent_name;
var    parent_contact = result[0].parent_contact;
var    kins_name = result[0].kins_name;
var    kins_contact = result[0].kins_contact;
var    bcf = result[0].bcf;
var    asf = result[0].asf;
var    other_payments = result[0].other_payments;
var    total_fees = result[0].total_fees;
var    tatal_paid = result[0].tatal_paid;
var    balance = result[0].balance;
var    other_payments_names = result[0].other_payments_names;
var   lin = "AD595L2342145";




//$(".student_name").html(student_name);
$("#fees_balance").html(balance.toLocaleString('en-US'));


// ...........Date ......................
$.ajax({
  url: 'https://gnyxug.com/api/date/kampala/',
  async : false,  //Enables results in gloaba variable
}).done(function(response2){
  result2 = JSON.parse(response2)
//console.log(student_number)

}).fail(function(error){
  console.log(error)
});

var   day = result2.day;
var   month = result2.month;
var   month_name = result2.month_name;
var   year = result2.year;
$("#day").html(day);
$("#month").html(month_name);
$("#year").html(year);


 ////////////////// Events //////////////////
 $.ajax({
  url: 'https://riseandshinehighschoolntinda.com/post/students_portal/events.php?all_events',
  success: function(result){

    if ($.trim(result) == '' ) {
      /// No data
  }
  else{
    var data_obj = JSON.parse(result);
    var obj_legnth = data_obj.length;
    for(i=0;i<obj_legnth;i++){


      var html = '<div class="d-flex gap-3 gap-lg-1 gap-xxl-3 justify-content-start mb-1 mb-lg-1 mb-xxl-1 p-1 pe-lg-1 pe-xxl-1 ps-lg-1 ps-xxl-1 px-lg-2 px-xxl-4">'+
     '<div class="border-2 border-end border-secondary d-flex pe-2">'+
     '<div class="me-2"><span class="badge bg-label-primary p-2"><i class="fa fa-calendar-o fa-lg"></i></span>'+
     '</div><div class="d-flex flex-column"><small>'+data_obj[i].month+'</small>'+
     '<h6 class="mb-0">'+data_obj[i].day+' </h6></div></div>'+
     '<div class="d-inline-flex justify-content-start text-start">'+
     '<div class="flex-column text-start"><small class="text-start">'+data_obj[i].description+'</small>'+
     '</div></div></div>';

      $("#events").append(html);
  }

  }
}
});

// ...........Upcoming Event ......................
$.ajax({
  url: 'https://riseandshinehighschoolntinda.com/post/students_portal/events.php?upcoming',
  async : false,  //Enables results in gloaba variable
}).done(function(response3){
  result3 = JSON.parse(response3)
//console.log(student_number)

}).fail(function(error){
  console.log(error)
});

var   day = result3[0].day;
var   month = result3[0].month;
var   event_titile = result3[0].event_titile;

$("#upcoming_day").html(day);
$("#upcoming_month").html(month);
$("#upcoming_event_titile").html(event_titile);

//// Pending Tickets //////
$.ajax({
  url: 'https://riseandshinehighschoolntinda.com/post/students_portal/tickets.php?pending',
  data:{
    student_number:student_number
  },
  success: function(result){

      var data_obj = JSON.parse(result);
      var obj_legnth = data_obj.length;
      for(i=0;i<obj_legnth;i++){

        $("#pending_tickets").html(obj_legnth);

      }
  }
});

////////////////// Noticeboard Slides //////////////////
$(document).ready(function() {
  $.ajax({
    url: 'https://www.riseandshinehighschoolntinda.com/post/students_portal/noticeboard.php', // PHP script to fetch images
    success: function(response) {
       var  data = JSON.parse(response)
       var obj_legnth = data.length

          console.log(data);

          for(i=0;i<obj_legnth;i++){


            if(i=="0"){
              var html ='<div class="carousel-item active"><img src="https://riseandshinehighschoolntinda.com/portal_noticeboard/'+data[i]+'"'+
              'class="w-100"/></div>';
            }
            else{
              var html ='<div class="carousel-item"><img src="https://riseandshinehighschoolntinda.com/portal_noticeboard/'+data[i]+'"'+
              'class="w-100"/></div>';

            }

            $('#slides').append(html);

          }


    },
    error: function(error) {
      console.error('Error fetching images:', error);
    }
  });
});
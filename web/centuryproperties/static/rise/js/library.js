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

function open_resource(url,title){

  $("#iframe_viewer").attr("src",url);
  $("#title").html(title);


    $("#viewer").modal('show');

}

///////////////////////// All books /////////////////
$.ajax({
  url: 'https://riseandshinehighschoolntinda.com/post/students_portal/library.php?all_resources',
  data:{
    student_class:student_class
  },
  success: function(result){

      var data_obj = JSON.parse(result);
      var obj_legnth = data_obj.length;
      for(i=0;i<obj_legnth;i++){

        var html ='<div onclick="open_resource(\''+data_obj[i].url+'\',\''+data_obj[i].title+'\')" class="col-6 col-lg-6 col-md-12 col-xl-2 mb-4"> <div class="card"><div class="card-body text-center">'+
        '<i class="fa fa-3x fa-file-powerpoint-o"></i><span class="d-block fw-semibold mb-1 text-center">'+data_obj[i].title+'</span>'+
        '<small class="text-success fw-semibold">&nbsp;</small></div></div></div>';

        $("#books").append(html);

      }
  }
});


//////////////////////// Modal Close      ///////////////
$(".modal_close").click(function(){

  var url ="";
  var title = "";

  $("#iframe_viewer").attr("src",url);
  $("#title").html(title);

  $("#viewer").modal('hide');

});

//// Hover over search results
$('.result').hover(
  function() {

    $(this).addClass('palm-cursor');
  },
  function() {
    $(this).removeClass('palm-cursor');
  }
);


///////////// Search ////////////////

$("#search_input").keypress(function(event) {
  if (event.which === 13) {

    var search_input = $("#search_input").val();
    if(!search_input==""){

     // console.log(search_input);
      $.ajax({
        url: 'https://riseandshinehighschoolntinda.com/post/students_portal/search.php',
        data:{
          search:search_input
        },
        success: function(result){
          $("#books").empty();
            var data_obj = JSON.parse(result);
            console.log(data_obj);
            var obj_legnth = data_obj.length;
            for(i=0;i<obj_legnth;i++){

            console.log(data_obj[i].type);
              if(data_obj[i].type == "pdf"){
                var html='<div class="col-md-4 col-xl-12 mb-1 me-2 ms-2 mt-1" data-pg-collapsed>'+
                '<h4 style="font-size:1.1rem" onclick="open_resource(\''+data_obj[i].url+'\',\''+data_obj[i].title+'\')" class="mb-1 result text-primary"><i class="fa fa-file-pdf-o"></i>&nbsp;'+data_obj[i].title+'</h4>' +
                '<p style="font-size:0.9rem" class="mb-0">'+data_obj[i].description+'</p>'+
                ' <p style="font-size:0.8rem">User group: '+data_obj[i].level+' Level</p> </div>';
              }
              else if(data_obj[i].type == "web"){
                var html='<div class="col-md-4 col-xl-12 mb-1 me-2 ms-2 mt-1" data-pg-collapsed>'+
                '<h4 style="font-size:1.1rem" onclick="open_resource(\''+data_obj[i].url+'\',\''+data_obj[i].title+'\')" class="mb-1 result text-primary"><i class="fa fa-globe"></i>&nbsp;'+data_obj[i].title+'</h4>' +
                '<p class="mb-0">'+data_obj[i].description+'</p>'+
                ' <p>User group: '+data_obj[i].level+' Level</p> </div>';
              }
              else if(data_obj[i].type == "yt"){
                var html='<div class="col-md-4 col-xl-12 mb-1 me-2 ms-2 mt-1" data-pg-collapsed>'+
                '<h4 style="font-size:1.1rem" onclick="open_resource(\''+data_obj[i].url+'\',\''+data_obj[i].title+'\')" class="mb-1 result text-primary"><i class="fa fa-youtube-play"></i>&nbsp;'+data_obj[i].title+'</h4>' +
                '<p class="mb-0">'+data_obj[i].description+'</p>'+
                ' <p>User group: '+data_obj[i].level+' Level</p> </div>';
              }

              $("#books").append(html);

            }
        }
      });




    }
    else{
      console.log("Search field is empty");

    }






  }
});

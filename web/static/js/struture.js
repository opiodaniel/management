// acGroup --
function acGroupCreator(parent){this.parent=parent;this.fields=[];this.members_list={"entity_number":[], "record_id":[]};
                                this.active_record_id=-1;this.is_group_updated=false}

acGroupCreator.prototype.get_entity_list = function(e_dic)
{
 var dic=this.parent.data;
 //alert("90100-1\n"+JSON.stringify(dic));
 var obj_number=dic["properties"]["obj_number"]
 var container_id=dic["container_id"]
 var e=e_dic["e"];var c=e_dic["c"];
 var table=dic["properties"]["table"];
 var field=dic["properties"]["field"]
 var value_field = dic["properties"]["value_field"]
 //alert(e.outerHTML)
 if(e.getAttribute("my_members_status")=="empty")
 {
     e.setAttribute("my_members_status", "filled")
     //alert(e.getAttribute("link"))
     var dic_=eval(e.getAttribute("link"))
     //alert("901540-24 acGroupCreator\n"+JSON.stringify(dic_));
     for(var i in dic_)
     {
      var id_=i; var title_=dic_[i]["title"];
      var s='&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' //<span style="cursor: pointer">+</span>'
      s+='<input type="checkbox" my_creator_number="'+obj_number+'" container_id="'+container_id+'" id="soldier_'+id_+'" soldier_number="'+id_+'" record_id="new" value="" table="'+table
      s+='" field="'+field+'" value_field="'+value_field+'" type_="groups">'
      s+='<label>'+title_+'</label><br/>'
      c.innerHTML+=s
     }
 }
}

acGroupCreator.prototype.create_obj = function()
{
  var dic=this.parent.data;var pp_=dic["properties"];
  var field=dic["properties"]["field"]; this.fields.push(field);
  var value_field=dic["properties"]["value_field"]; this.fields.push(value_field);
  var container = document.getElementById("content_"+dic["container_id"]);
   //alert("90100-2 acGroupCreator.prototype.create_obj\n"+JSON.stringify(dic));
  var obj_number = dic["properties"]["obj_number"]
  this.main_div=document.createElement("div");
  this.main_div.my_creator_obj=this;
  this.main_div.dic=dic;
  this.main_div.setAttribute("id", obj_number);
  this.main_div.setAttribute("obj_type", dic["obj_type"]);
  this.main_div.setAttribute("type", dic["element_name"]);
  var style_ = "position:absolute;left:"+pp_["x"]+"px;top:"+pp_["y"]+"px;"

  var width_=pp_["width"]; if(width_==null || width_==""){width_=200};style_+="width:"+width_+"px;"
  //var height_=pp_["height"]; if(height_==null || height_==""){height_=300};

  var bs_=pp_["border_style"];if(bs_!=null && bs_!=""){style_+="border-style:"+bs_+";"}
  var bw_=pp_["border_width"];if(bw_!=null && bw_!=""){style_+="border-width:"+bw_+"px;"}
  var bc_=pp_["border_color"];if(bc_!=null && bc_!=""){style_+="border-color:"+bc_+";"}
  var br_=pp_["border_radius"];if(br_!=null && br_!=""){style_+="border-radius:"+br_+"px;"}
  var c_=pp_["color"];if(c_!=null && c_!=""){style_+="color:"+c_+";"}
  var bgc_=pp_["background_color"];if(bgc_!=null && bgc_!=""){style_+="background-color:"+bgc_+";"}

//alert(style_)

  this.main_div.setAttribute("style", style_);
  this.main_div.setAttribute("class", "row");
  this.main_div.setAttribute("container_id", dic["container_id"]);

  this.main_div.addEventListener("change", function(event){
      var e=event.target;
   //alert("90100-3 change\n\n"+e.outerHTML)
  })

  this.main_div.addEventListener("click", function(event){
      var e=event.target;
      //alert("click: \n\n"+this.outerHTML)
      //alert("click: \n\n"+e.outerHTML)
      //alert("90100-4\n"+JSON.stringify(this.dic["properties"]));

      //alert(pp_["obj_number"]+"\n"+JSON.stringify(this.dic["properties"]))

      var my_class_members=e.getAttribute("my_class_members"+pp_["obj_number"])

      //alert("90142-2 acGroupCreator.prototype.create_obj\n"+JSON.stringify(this.dic));
      //alert(this.dic["properties"]["present"])
  try{
      if(my_class_members!=null){
        //alert(this.dic["properties"]["present"])
        var c = document.getElementsByClassName(my_class_members)[0]
        var etype_=e.getAttribute("type")
        if(etype_=="checkbox"){
        try{
          if(this.dic["properties"]["present"]=="detail")
          {
             //alert(e.outerHTML)
             //alert(e.checked)
             var cc=c.getElementsByTagName("input");
             var ec=new Event("change", {bubbles: true});
             var n_=0
             for(k in cc)
             {
              cc[k].checked=e.checked;
             }
             for(k in cc)
             {
             //alert(cc[k].outerHTML)

              cc[k].dispatchEvent(ec)
             }
          }
        } catch(er){"Error 550: "+er}
        } else if (etype_=="span"){
        //alert(999)
        //alert(c.outerHTML)
        //alert(c.style.display)

          if(c.style.display=="block"){c.style.display="none"}else{c.style.display="block";
          if(this.dic["properties"]["present"]=="detail")
          {
            this.my_creator_obj.get_entity_list({"e":e,"c":c})}
          }
        }

      } else{
        var etype_=e.getAttribute("type")
        if(etype_=="checkbox"){
         //alert("group55")
         this.my_creator_obj.obj_was_clicked(e)
        }
      }

} catch(er){alert("Error 555\n"+er)}

  })
  container.appendChild(this.main_div);
  //--
  var general_dic_name=dic["properties"]["setup_dictionary"]
  if(general_dic_name==null || general_dic_name==""){this.main_div.innerHTML="Group Pluging"}
  else {this.main_div.innerHTML="Group Pluging working"}
  //--
  for(f in dic["functions"]){var s="this.main_div."+f+"="+dic["functions"][f];eval(s);}
 // alert(this.main_div.outerHTML)
}
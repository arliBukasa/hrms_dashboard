odoo.define('hrms_dashboard.Dashboard_font', function (require) {

    "use strict";
    //personalisation du formulaire
    //Chargement du document 
    $(document).ready(function () {

        $('#button_id').click(function (e) {
            console.clear();
            console.log("here i am in the function"); 
           

            var container_block;
            var card_body;
            // Contenaire du poste
            container_block = document.getElementById('myCollapse');
            // 
            var x = document.getElementById("to_add");
            // Creation du nouvel objet (poste à ajouter)
            x.childNodes[3].classList.remove("show");
            var y=x.cloneNode(true);

            var lien1=x.childNodes[1];
            lien1.ariaExpanded="false";
            
            var cles=container_block.children.length
            y.id=cles;
            var lien=y.childNodes[1];
            lien.dataset.target="#myCollapseTab"+cles;
            lien.innerHTML = 'POSTE '+cles;
            console.log(y.id);
            console.log( y.children);

            var collapse = y.children[1];

            collapse.setAttribute("id", "myCollapseTab"+cles);
            collapse.id="myCollapseTab"+cles;

            console.log("le premier enfant");
            var laPosition=container_block.children[container_block.children.length-1];
            console.log(laPosition);

            console.log("x et y");
            console.log(y);
            console.log(x);
            // insertion de du poste
            try {
                for (var i=0;i<container_block.children.length-1;i++){
                    if (container_block.children[i].children !== undefined){
                        container_block.children[i].children[1].classList.remove("show");
                        console.log(container_block.children[i].children[1]);

                    }

                };               
                
                laPosition.before(y);
                var second=y.children[1];
                second.classList.add("show");
                console.log("les enfants du poste");
                console.log(y.children);
                e.preventDefault();
                document.location.assign("#to_add");
                document.location.href="#to_add";
                console.log(document.location);
                
            } catch (error) {
                console.log(error);
            }

            
             
        });
        $('#button_ed').click(function (e) {
            console.clear();
            console.log("here i am in the function"); 
           

            var container_block;
            var card_body;
            // Contenaire du poste
            container_block = document.getElementById('myCollapse_ed');
            // 
            var x = document.getElementById("to_add_ed");
            // Creation du nouvel objet (poste à ajouter)
            x.childNodes[3].classList.remove("show");
            var y=x.cloneNode(true);

            var lien1=x.childNodes[1];
            lien1.ariaExpanded="false";
            
            var cles=container_block.children.length
            y.id=cles;
            var lien=y.childNodes[1];
            lien.dataset.target="#myCollapseTab_ed"+cles;
            lien.innerHTML = 'PARCOURS '+cles;
            console.log(y.id);
            console.log( y.children);

            var collapse = y.children[1];

            collapse.setAttribute("id", "myCollapseTab_ed"+cles);
            collapse.id="myCollapseTab_ed"+cles;

            console.log("le premier enfant");
            var laPosition=container_block.children[container_block.children.length-1];
            console.log(laPosition);

            console.log("x et y");
            console.log(y);
            console.log(x);
            // insertion de du poste
            try {
                for (var i=0;i<container_block.children.length-1;i++){
                    if (container_block.children[i].children !== undefined){
                        container_block.children[i].children[1].classList.remove("show");
                        console.log(container_block.children[i].children[1]);

                    }

                };               
                
                laPosition.before(y);
                var second=y.children[1];
                second.classList.add("show");
                console.log("les enfants du poste");
                console.log(y.children);
                e.preventDefault();
                document.location.assign("#to_add_ed");
                document.location.href="#to_add_ed";
                console.log(document.location);
                
            } catch (error) {
                console.log(error);
            }

            
             
        });
        $('#button_for').click(function (e) {
            console.clear();
            console.log("here i am in the function"); 
           

            var container_block;
            var card_body;
            // Contenaire du poste
            container_block = document.getElementById('myCollapse_for');
            // 
            var x = document.getElementById("to_add_for");
            // Creation du nouvel objet (poste à ajouter)
            x.childNodes[3].classList.remove("show");
            var y=x.cloneNode(true);

            var lien1=x.childNodes[1];
            lien1.ariaExpanded="false";
            
            var cles=container_block.children.length
            y.id=cles;
            var lien=y.childNodes[1];
            lien.dataset.target="#myCollapseTab_for"+cles;
            lien.innerHTML = 'FORMATION '+cles;
            console.log(y.id);
            console.log( y.children);

            var collapse = y.children[1];

            collapse.setAttribute("id", "myCollapseTab_for"+cles);
            collapse.id="myCollapseTab_for"+cles;

            console.log("le premier enfant");
            var laPosition=container_block.children[container_block.children.length-1];
            console.log(laPosition);

            console.log("x et y");
            console.log(y);
            console.log(x);
            // insertion de du poste
            try {
                for (var i=0;i<container_block.children.length-1;i++){
                    if (container_block.children[i].children !== undefined){
                        container_block.children[i].children[1].classList.remove("show");
                        console.log(container_block.children[i].children[1]);

                    }

                };               
                
                laPosition.before(y);
                var second=y.children[1];
                second.classList.add("show");
                console.log("les enfants du poste");
                console.log(y.children);
                e.preventDefault();
                document.location.assign("#to_add_for");
                document.location.href="#to_add_for";
                console.log(document.location);
                
            } catch (error) {
                console.log(error);
            }

            
             
        });
        $('#button_comp').click(function (e) {
            console.clear();
            console.log("here i am in the function"); 
           

            var container_block;
            var card_body;
            // Contenaire du poste
            container_block = document.getElementById('myCollapse_comp');
            // 
            var x = document.getElementById("to_add_comp");
            // Creation du nouvel objet (poste à ajouter)
            x.childNodes[3].classList.remove("show");
            var y=x.cloneNode(true);

            var lien1=x.childNodes[1];
            lien1.ariaExpanded="false";
            
            var cles=container_block.children.length
            y.id=cles;
            var lien=y.childNodes[1];
            lien.dataset.target="#myCollapseTab_comp"+cles;
            lien.innerHTML = 'COMPTETENCE '+cles;
            console.log(y.id);
            console.log( y.children);

            var collapse = y.children[1];

            collapse.setAttribute("id", "myCollapseTab_comp"+cles);
            collapse.id="myCollapseTab_comp"+cles;

            console.log("le premier enfant");
            var laPosition=container_block.children[container_block.children.length-1];
            console.log(laPosition);

            console.log("x et y");
            console.log(y);
            console.log(x);
            // insertion de du poste
            try {
                //remove showing
                for (var i=0;i<container_block.children.length-1;i++){
                    if (container_block.children[i].children !== undefined){
                        container_block.children[i].children[1].classList.remove("show");
                        console.log(container_block.children[i].children[1]);
                    }

                };               
                
                laPosition.before(y);
                var second=y.children[1];
                second.classList.add("show");
                console.log("les enfants du poste");
                console.log(y.children);

                //Gestion automatique des etoiles et le niveau
                var rate_c_text_conte=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[0]);
                var star1=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[1]);
                var star2=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[2]);
                var star3=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[3]);
                var star4=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[4]);
                var star5=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[5]);
                var input_niv_c=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[6]);
                var niveau_parent=(((((second.children[0]).children[0]).children[1]).children[0]).children[0]);
                
                niveau_parent.id="comp_rate"+cles;
                star1.id= "i_c_20_"+cles;
                star1.href= "#i_c_20_"+cles;
                star2.id= "i_c_40_"+cles;
                star2.href= "#i_c_40_"+cles;
                star3.id= "i_c_60_"+cles;
                star3.href= "#i_c_60_"+cles;
                star4.id= "i_c_80_"+cles;
                star4.href= "#i_c_80_"+cles;
                star5.id= "i_c_100_"+cles;
                star5.href= "#i_c_100_"+cles;
                input_niv_c.id="niveau_comp_"+cles;
                rate_c_text_conte.id="rate_c_text"+cles;


                star1.click(function (e) {
                    e.preventDefault();
                    console.log("=======niveau cliqué=====");
                    console.log(niveau[i]);
                    console.log(self);
                    var niv=document.getElementById("niveau_comp_"+cles);
                    niv.value=niveau[i];
                    // remplissage des etoiles
                    var rate= document.getElementById("comp_rate"+cles);
                    for (let j = 0; j <=4; j++) {
                        console.log("=======compteur i et j=====");
                        console.log(i);
                        console.log(j);
                        if(i!=j){
                        rate.classList.remove("s_rating_"+(j+1));
                        rate.classList.remove("s_rating_"+(j));
                        console.log("======I et J differents=====");
                        console.log(rate);
                        }
                        if(i==j){
                            rate.classList.add("s_rating_"+(j+1));
                            console.log("======I = J =====");
                            console.log(rate); 
                        }
                    }
                      // changement de text niveau
                      var txt_niveau= document.getElementById("rate_c_text"+cles);
                      txt_niveau.innerHTML="<strong>Niveau"+ niveau[i]+"</strong>";
                    
                      console.log("======les valeurs des niveaux=====");
                    console.log(rate);
                    console.log(txt_niveau);
                    console.log(niv);

                });
                star2.click(function (e) {
                    e.preventDefault();
                    console.log("=======niveau cliqué=====");
                    console.log(niveau[i]);
                    console.log(self);
                    var niv=document.getElementById("niveau_comp_"+cles);
                    niv.value=niveau[i];
                    // remplissage des etoiles
                    var rate= document.getElementById("comp_rate"+cles);
                    for (let j = 0; j <=4; j++) {
                        console.log("=======compteur i et j=====");
                        console.log(i);
                        console.log(j);
                        if(i!=j){
                        rate.classList.remove("s_rating_"+(j+1));
                        rate.classList.remove("s_rating_"+(j));
                        console.log("======I et J differents=====");
                        console.log(rate);
                        }
                        if(i==j){
                            rate.classList.add("s_rating_"+(j+1));
                            console.log("======I = J =====");
                            console.log(rate); 
                        }
                    }
                      // changement de text niveau
                      var txt_niveau= document.getElementById("rate_c_text"+cles);
                      txt_niveau.innerHTML="<strong>Niveau"+ niveau[i]+"</strong>";
                    
                      console.log("======les valeurs des niveaux=====");
                    console.log(rate);
                    console.log(txt_niveau);
                    console.log(niv);

                });
                star3.click(function (e) {
                    e.preventDefault();
                    console.log("=======niveau cliqué=====");
                    console.log(niveau[i]);
                    console.log(self);
                    var niv=document.getElementById("niveau_comp_"+cles);
                    niv.value=niveau[i];
                    // remplissage des etoiles
                    var rate= document.getElementById("comp_rate"+cles);
                    for (let j = 0; j <=4; j++) {
                        console.log("=======compteur i et j=====");
                        console.log(i);
                        console.log(j);
                        if(i!=j){
                        rate.classList.remove("s_rating_"+(j+1));
                        rate.classList.remove("s_rating_"+(j));
                        console.log("======I et J differents=====");
                        console.log(rate);
                        }
                        if(i==j){
                            rate.classList.add("s_rating_"+(j+1));
                            console.log("======I = J =====");
                            console.log(rate); 
                        }
                    }
                      // changement de text niveau
                      var txt_niveau= document.getElementById("rate_c_text"+cles);
                      txt_niveau.innerHTML="<strong>Niveau"+ niveau[i]+"</strong>";
                    
                      console.log("======les valeurs des niveaux=====");
                    console.log(rate);
                    console.log(txt_niveau);
                    console.log(niv);

                });
                star4.click(function (e) {
                    e.preventDefault();
                    console.log("=======niveau cliqué=====");
                    console.log(niveau[i]);
                    console.log(self);
                    var niv=document.getElementById("niveau_comp_"+cles);
                    niv.value=niveau[i];
                    // remplissage des etoiles
                    var rate= document.getElementById("comp_rate"+cles);
                    for (let j = 0; j <=4; j++) {
                        console.log("=======compteur i et j=====");
                        console.log(i);
                        console.log(j);
                        if(i!=j){
                        rate.classList.remove("s_rating_"+(j+1));
                        rate.classList.remove("s_rating_"+(j));
                        console.log("======I et J differents=====");
                        console.log(rate);
                        }
                        if(i==j){
                            rate.classList.add("s_rating_"+(j+1));
                            console.log("======I = J =====");
                            console.log(rate); 
                        }
                    }
                      // changement de text niveau
                      var txt_niveau= document.getElementById("rate_c_text"+cles);
                      txt_niveau.innerHTML="<strong>Niveau"+ niveau[i]+"</strong>";
                    
                      console.log("======les valeurs des niveaux=====");
                    console.log(rate);
                    console.log(txt_niveau);
                    console.log(niv);

                });
                star5.click(function (e) {
                    e.preventDefault();
                    console.log("=======niveau cliqué=====");
                    console.log(niveau[i]);
                    console.log(self);
                    var niv=document.getElementById("niveau_comp_"+cles);
                    niv.value=niveau[i];
                    // remplissage des etoiles
                    var rate= document.getElementById("comp_rate"+cles);
                    for (let j = 0; j <=4; j++) {
                        console.log("=======compteur i et j=====");
                        console.log(i);
                        console.log(j);
                        if(i!=j){
                        rate.classList.remove("s_rating_"+(j+1));
                        rate.classList.remove("s_rating_"+(j));
                        console.log("======I et J differents=====");
                        console.log(rate);
                        }
                        if(i==j){
                            rate.classList.add("s_rating_"+(j+1));
                            console.log("======I = J =====");
                            console.log(rate); 
                        }
                    }
                      // changement de text niveau
                      var txt_niveau= document.getElementById("rate_c_text"+cles);
                      txt_niveau.innerHTML="<strong>Niveau"+ niveau[i]+"</strong>";
                    
                      console.log("======les valeurs des niveaux=====");
                    console.log(rate);
                    console.log(txt_niveau);
                    console.log(niv);

                });

                //Niveaux des Competenaces

                var niveau =[20,40,60,80,100];
                var etoiles=$(".etoile-c");
                console.log(etoiles);
                
                for(var i = 0; i < etoiles.length; i++) {
                    var etoile = etoiles[i];
                    console.log("etoile");
                    console.log(etoile);
                    etoile.onclick = function(e) {
                        for (let j = 0; j <=4; j++) {
                            e.target.parentNode.classList.remove("s_rating_"+j); 
                        } 
                        let tableau_objet=e.target.id.split("_");
                        let classetoile= (tableau_objet[2])/20;
                        input_niv_c.value=classetoile*20;  
                        e.target.parentNode.classList.add("s_rating_"+classetoile);
                        console.log("============le texte du nineau ==============");
                        e.target.parentNode.children[0].children[0].innerHTML="Niveau "+ classetoile*20
                        console.log(e.target.parentNode.children[0].children[0]);
                        
                        console.log("============l'element cliqué ==============");
                        console.log(tableau_objet);
                        console.log(classetoile);
                        document.location.assign(e.target);  
                                           
                    }
                }
                
                console.log("============star 1-5 ==============");
                console.log(star1);
                console.log(star2);
                console.log(star3);
                console.log(star4);
                console.log(star5);

                e.preventDefault();
                document.location.assign(e.target);
                console.log(document.location);
           
            } catch (error) {
                console.log(error);
            }

        });
        $('#button_lang').click(function (e) {
            console.clear();
            console.log("here i am in the function"); 
           

            var container_block;
            var card_body;
            // Contenaire du poste
            container_block = document.getElementById('myCollapse_lang');
            // 
            var x = document.getElementById("to_add_lang");
            // Creation du nouvel objet (poste à ajouter)
            x.childNodes[3].classList.remove("show");
            var y=x.cloneNode(true);

            var lien1=x.childNodes[1];
            lien1.ariaExpanded="false";
            
            var cles=container_block.children.length
            y.id=cles;
            var lien=y.childNodes[1];
            lien.dataset.target="#myCollapseTab_lang"+cles;
            lien.innerHTML = 'LANGUE '+cles;
            console.log(y.id);
            console.log( y.children);

            var collapse = y.children[1];

            collapse.setAttribute("id", "myCollapseTab_lang"+cles);
            collapse.id="myCollapseTab_lang"+cles;

            console.log("le premier enfant");
            var laPosition=container_block.children[container_block.children.length-1];
            console.log(laPosition);

            console.log("x et y");
            console.log(y);
            console.log(x);
            // insertion de du poste
            try {
                for (var i=0;i<container_block.children.length-1;i++){
                    if (container_block.children[i].children !== undefined){
                        container_block.children[i].children[1].classList.remove("show");
                        console.log(container_block.children[i].children[1]);

                    }

                };               
                
                laPosition.before(y);
                var second=y.children[1];
                second.classList.add("show");
                console.log("les enfants du poste");
                console.log(y.children);
                e.preventDefault();
                document.location.assign(e.target);
                document.location.href="#to_add_lang";
                console.log(document.location);
                var input_niv_l=((((((second.children[0]).children[0]).children[1]).children[0]).children[0]).children[6]);
                input_niv_l.id="niveau_lang_"+cles
                
                console.log("input");
                console.log(input_niv_l);
                //Niveaux des Langues

                var niveau =[20,40,60,80,100];
                var etoiles=$(".etoile-l");
                console.log(etoiles);
                
                for(var i = 0; i < etoiles.length; i++) {
                    var etoilel = etoiles[i];
                    console.log("etoile");
                    console.log(etoilel);
                    etoilel.onclick = function(e) {
                        for (let j = 0; j <=4; j++) {
                            e.target.parentNode.classList.remove("s_rating_"+j); 
                        } 
                        let tableau_objetl=e.target.id.split("_");
                        let classetoilel= (tableau_objetl[2])/20;
                        input_niv_l.value=classetoilel*20;
                        e.target.parentNode.classList.add("s_rating_"+classetoilel);
                        console.log("============le texte du nineau ==============");
                        e.target.parentNode.children[0].children[0].innerHTML="Niveau "+ classetoilel*20
                        console.log(e.target.parentNode.children[0].children[0]);
                        
                        console.log("============l'element cliqué ==============");
                        console.log(tableau_objetl);
                        console.log(classetoilel);
                        document.location.assign(e.target);  
                                          
                    }
                }
            } catch (error) {
                console.log(error);
            }

            
             
        });

// Gestion des etoiles dans le rates
        //Niveaux des langues
        $('#i_l_20_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_lang_1");
                niv.value=20;
                // remplissage des etoiles
                var rate1= document.getElementById("lang_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_3");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_5");
                rate1.classList.add("s_rating_1");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_l_text");
                txt_niveau.innerHTML="<strong>Niveau 20</strong>";


             });
        $('#i_l_40_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_lang_1");
                niv.value=40;
                // remplissage des etoiles
                var rate1= document.getElementById("lang_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.add("s_rating_2");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_3");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_5");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_l_text");
                txt_niveau.innerHTML="<strong>Niveau 40</strong>";


             });
        $('#i_l_60_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_lang_1");
                niv.value=60;
                // remplissage des etoiles
                var rate1= document.getElementById("lang_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_5");
                rate1.classList.add("s_rating_3");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_l_text");
                txt_niveau.innerHTML="<strong>Niveau 60</strong>";


             });
        $('#i_l_80_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_lang_1");
                niv.value=80;
                // remplissage des etoiles
                var rate1= document.getElementById("lang_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_3");
                rate1.classList.remove("s_rating_5");
                rate1.classList.add("s_rating_4");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_l_text");
                txt_niveau.innerHTML="<strong>Niveau 80</strong>";


             });
        $('#i_l_100_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_lang_1");
                niv.value=100;
                // remplissage des etoiles
                var rate1= document.getElementById("lang_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_3");
                rate1.classList.add("s_rating_5");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_l_text");
                txt_niveau.innerHTML="<strong>Niveau 100</strong>";


             });

        //Niveaux des Competenaces
        $('#i_c_20_1').click(function (e) {
            e.preventDefault();
            var niv=document.getElementById("niveau_comp_1");
            niv.value=20;
            // remplissage des etoiles
            var rate1= document.getElementById("comp_rate1");
            rate1.classList.remove("s_rating_0");
            rate1.classList.remove("s_rating_3");
            rate1.classList.remove("s_rating_2");
            rate1.classList.remove("s_rating_4");
            rate1.classList.remove("s_rating_5");
            rate1.classList.add("s_rating_1");
            console.log(rate1);
            // changement de text niveau
            var txt_niveau= document.getElementById("rate_c_text");
            txt_niveau.innerHTML="<strong>Niveau 20</strong>";
         });
        $('#i_c_40_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_comp_1");
                niv.value=40;
                // remplissage des etoiles
                var rate1= document.getElementById("comp_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.add("s_rating_2");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_3");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_5");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_c_text");
                txt_niveau.innerHTML="<strong>Niveau 40</strong>";


            });
        $('#i_c_60_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_comp_1");
                niv.value=60;
                // remplissage des etoiles
                var rate1= document.getElementById("comp_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_5");
                rate1.classList.add("s_rating_3");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_c_text");
                txt_niveau.innerHTML="<strong>Niveau 60</strong>";


            });
        $('#i_c_80_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_comp_1");
                niv.value=80;
                // remplissage des etoiles
                var rate1= document.getElementById("comp_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_3");
                rate1.classList.remove("s_rating_5");
                rate1.classList.add("s_rating_4");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_c_text");
                txt_niveau.innerHTML="<strong>Niveau 80</strong>";


            });
        $('#i_c_100_1').click(function (e) {
                e.preventDefault();
                var niv=document.getElementById("niveau_comp_1");
                niv.value=100;
                // remplissage des etoiles
                var rate1= document.getElementById("comp_rate1");
                rate1.classList.remove("s_rating_0");
                rate1.classList.remove("s_rating_1");
                rate1.classList.remove("s_rating_2");
                rate1.classList.remove("s_rating_4");
                rate1.classList.remove("s_rating_3");
                rate1.classList.add("s_rating_5");
                console.log(rate1);
                // changement de text niveau
                var txt_niveau= document.getElementById("rate_c_text");
                txt_niveau.innerHTML="<strong>Niveau 100</strong>";


            });
                
             
            
        
       
    });

});
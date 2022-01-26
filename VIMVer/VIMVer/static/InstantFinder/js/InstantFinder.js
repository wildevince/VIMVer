$(document).ready(function() {

    $("#outBlastList").each(function(){
        $(this).html($(this).children('div').sort(function(a,b){
            return (Number($(b).attr('accession'))) < Number(($(a).attr('accession'))) ? 1 : -1;
        }));
    });

})
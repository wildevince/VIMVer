function getAll_td_byPosition(position) {
	var res = [];
	var All = document.getElementsByTagName('td');
	Array.from(All).forEach(cell => {
		if (cell.getAttribute('data-position') == position) {
			 res.push(cell)
		}
	});
	return res;
}


$(document).ready(function() {

	var all_td = document.getElementsByTagName('td');

	Array.from(all_td).forEach(cell => {
		var position = cell.getAttribute('data-position');

		cell.addEventListener("mouseover", function(event) {
			event.target.setAttribute('hover', 'true')
			let samePositionnedCell = getAll_td_byPosition(position);
			samePositionnedCell.forEach(residu => {
				residu.setAttribute('hover', 'true');
			});
		});

		cell.addEventListener("mouseout", function(event) {
			event.target.setAttribute('hover', 'true')
			let samePositionnedCell = getAll_td_byPosition(position);
			samePositionnedCell.forEach(residu => {
				residu.removeAttribute('hover', 'false');
			});
		});

	});
	
	$(function() {
		$("div.p-row").tooltip({track:true});
		});

	/*
	$("#infobox-help").each.click(function() {
		alert("infobox-help");
	});
	*/

	//$("#prot_display tr.refSeq td").

	/*
	function turn_InfoContent_off() {
		$(".infoContents div").all().Attr("hidden");
		};
	$("#infobox-help").click(function() {
		turn_InfoContent_off();
		$("#infocontent-help").removeAttr("hidden");
	});
	$("#infobox-project").click(function() {
		turn_InfoContent_off();
		$("#infocontent-project").removeAttr("hidden");
	});
	$("#infobox-contact").click(function() {
		turn_InfoContent_off();
		$("#infocontent-contact").removeAttr("hidden");
	});
	*/
	

})
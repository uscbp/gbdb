function deleteInlineForm(prefix, idx){
    document.getElementById('id_'+prefix+'-'+idx+'-DELETE').value='on';
    document.getElementById(prefix+'-'+idx).style.display='none';
    return false;
}

function showPopup(windowName, width, height, href)
{
    if (href.indexOf('?') == -1)
        href += '?_popup=1';
    else
        href  += '&_popup=1';
    var win = window.open(href, windowName, 'height='+height+',width='+width+',resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function updateCircle()
{
    // Add circle overlay and bind to marker
    var circle = new google.maps.Circle({
        map: map,
        radius: 16093,    // 10 miles in metres
        fillColor: '#AA0000'
    });
    circle.bindTo('center', marker, 'position');
}

function getTRTag(idx)
{
    if(idx%2==0)
        return 'even_row';
    else
        return 'odd_row';
}
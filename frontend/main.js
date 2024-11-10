data = null


async function get_data(res){
    let response = await fetch("/data/api/"+String(res)) // Don't have domain
    return response.json()
}

function create_cell(value){
    value = String(value)
    cell = document.createElement("td");
    cell.innerHTML=value
    return cell;
}


async function get_query_data(){
	//Get the select
    const dropbar = document.getElementById("drop-bar")
    const filter = document.getElementById("filter");
    if (filter.value == "")
        return "All"
    return `{\"${dropbar.value}\":\"${filter.value}\"}`;
}

function toggleRowExpansion(row, oib) {
        // Check if the row is already expanded
        if (row.nextElementSibling && row.nextElementSibling.classList.contains('expanded-row')) {
            // If expanded, remove the expanded row
            row.nextElementSibling.remove();
            return;
        }

        let obj = null;
        for (let i=0; i < data.length; i++){
            if (data[i].oib == oib){
                obj = data[i];
                break;
            }
        }
        // Otherwise, create the expanded row
        const expandedRow = document.createElement('tr');
        expandedRow.classList.add('expanded-row');

        // Create a cell that spans all columns
        const expandedCell = document.createElement('td');
        expandedCell.colSpan = row.cells.length;

        // Jelovnik table
        const jelovnik_table = document.createElement('table');
        jelovnik_table.classList.add('subtable');
        jelovnik_table.innerHTML = `
            <thead>
                <tr><th>Naziv</th><th>Namirnice</th><th>Kosher</th><th>Halal</th><th>Vegan</th></tr>
            </thead>
        `;

        let jelovnik_table_body = document.createElement("tbody")
        for (jelo of obj.jelovnik){
            jelovnik_table.innerHTML += `
                <tr>
                    <td>${jelo.naziv}</td>
                    <td>${jelo.namirnice}</td>
                    <td>${jelo.kosher}</td>
                    <td>${jelo.halal}</td>
                    <td>${jelo.vegan}</td>
                </tr>
            `;
        }                
        jelovnik_table.appendChild(jelovnik_table_body)
        expandedCell.appendChild(jelovnik_table);

        // Radnici table
        const radnici_table = document.createElement('table');
        radnici_table.classList.add('subtable');
        radnici_table.innerHTML = `
            <thead>
                <tr>
                    <th>Oib</th>
                    <th>Ime</th>
                    <th>Prezime</th>
                    <th>Uloga</th>
                    <th>Plaća</th>
                    <th>Valuta</th>
                    <th>Početak radnog odnosa</th>
                    <th>Kraj radnog odnosa</th></tr>
            </thead>
        `;

        let radnici_table_body = document.createElement("tbody")
        for (radnik of obj.radnici){
            radnici_table.innerHTML += `
                <tr>
                    <td>${radnik.oib}</td>
                    <td>${radnik.ime}</td>
                    <td>${radnik.prezime}</td>
                    <td>${radnik.uloga}</td>
                    <td>${radnik.plaća}</td>
                    <td>${radnik.valuta}</td>
                    <td>${radnik.početak_radnog_odnosa}</td>
                    <td>${radnik.kraj_radnog_odnosa}</td>
                </tr>
            `;
        }                
        radnici_table.appendChild(radnici_table_body)
        expandedCell.appendChild(radnici_table);

        // Radnici table
        const inspekcije_table = document.createElement('table');
        inspekcije_table.classList.add('subtable');
        inspekcije_table.innerHTML = `
            <thead>
                <tr>
                    <th>Datum</th>
                    <th>Oib inspektora</th>
                    <th>Ime inspektora</th>
                    <th>Prezime inspektora</th>
                    <th>Ocjena</th>
            </thead>
        `;

        let inspekcije_table_body = document.createElement("tbody")
        console.log(obj.inspekcije)
        for (inspekcija of obj.inspekcije){
            inspekcije_table.innerHTML += `
                <tr>
                    <td>${inspekcija.datum}</td>
                    <td>${inspekcija.inspektor.oib}</td>
                    <td>${inspekcija.inspektor.ime}</td>
                    <td>${inspekcija.inspektor.prezime}</td>
                    <td>${inspekcija.ocjena}</td>
                </tr>
            `;
        }                
        inspekcije_table.appendChild(inspekcije_table_body)
        expandedCell.appendChild(inspekcije_table);

        // Append the expanded cell to the expanded row
        expandedRow.appendChild(expandedCell);

        // Insert the expanded row right after the clicked row
        row.parentNode.insertBefore(expandedRow, row.nextSibling);
    }

function draw_data(){
    //Select tbody
    if (data == null)
        return
    let table = document.getElementById("data-body")
    table.innerHTML=""
    for (restoran of data){
        let row = document.createElement("tr")
	row.setAttribute("onClick", "toggleRowExpansion(this," + String(restoran.oib) + ");");
	row.setAttribute("id", String(restoran.oib));
        row.appendChild(create_cell(restoran.oib))
        row.appendChild(create_cell(restoran.ime))
        row.appendChild(create_cell(restoran.datum_otvaranja))
        row.appendChild(create_cell(restoran.datum_zatvaranja))
        row.appendChild(create_cell(restoran.google_recenzija))
        row.appendChild(create_cell(restoran.michelin_zvjezdica))
        row.appendChild(create_cell(restoran.lokacija.adresa))
        row.appendChild(create_cell(restoran.lokacija.grad))
        row.appendChild(create_cell(restoran.lokacija.drzava))
        row.appendChild(create_cell(restoran.lokacija.postanski_broj))
        row.appendChild(create_cell(restoran.vlasnik.oib))
        row.appendChild(create_cell(restoran.vlasnik.ime))
        row.appendChild(create_cell(restoran.vlasnik.prezime))
        table.appendChild(row)
    }
}


async function query(e){
	if (e.keyCode != 13)
		return null;
	data = await get_data(await get_query_data())
	draw_data()
}

async function main(){
    data = await get_data("All")
    draw_data()
}

function construct_csv(){
	let csv = `oib;ime;datum_otvaranja;datum_zatvaranja;google_recenzija;michelin_zvjezdica;vlasnik_oib;vlasnik_ime;vlasnik_prezime;inspektor_oib;inspektor_ime;oib_radnik;radnik_ime;radnik_prezime;plaća;valuta;početak_radnog_odnosa;kraj_radnog_odnosa;naziv;namirnice;kosher;halal;vegan
\n`;
	for ( rd of data ){
		let line =""
		line +=String(rd.oib)+";"
		line +=String(rd.ime)+";"
		line +=String(rd.datum_otvaranja)+";"
		line +=String(rd.datum_zatvaranja)+";"
		line +=String(rd.google_recenzija)+";"
		line +=String(rd.michelin_zvjezdica)+";"
		line +=String(rd.vlasnik_oib)+";"
		line +=String(rd.vlasnik_ime)+";"
                for ( inspekcija of rd.inspekcije ){
			 line += String(inspekcija.inspektor.oib) + ";"
			 line += String(inspekcija.inspektor.ime) + ";"
		}
                for ( radnik of rd.radnici ){
			 line += String(radnik.oib) + ";"
			 line += String(radnik.ime) + ";"
			 line += String(radnik.prezime) + ";"
			 line += String(radnik.plaća) + ";"
			 line += String(radnik.valuta) + ";"
			 line += String(radnik.početak_radnog_odnosa) + ";"
			 line += String(radnik.kraj_radnog_odnosa) + ";"
		}
		for ( jelo of rd.jelovnik ){
			 line += String(jelo.naziv) + ";"
			 line += String(jelo.namirnice) + ";"
			 line += String(jelo.kosher) + ";"
			 line += String(jelo.halal) + ";"
			 line += String(jelo.vegan) + ";"
		}
                csv +=line + "\n"
	}
	return csv;
}

function export_csv(){
	csv = construct_csv()
	let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(csv);
	let downloadAnchorNode = document.createElement('a');
	downloadAnchorNode.setAttribute("href",     dataStr);
	downloadAnchorNode.setAttribute("download", "kante.csv");
	document.body.appendChild(downloadAnchorNode); // required for firefox
	downloadAnchorNode.click();
	downloadAnchorNode.remove()
}

function export_json(){
	let new_tab = window.open('data:application/json,' + JSON.stringify(data));
}

main()

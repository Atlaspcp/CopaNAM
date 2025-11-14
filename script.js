// 1. Definición Inicial de Equipos y Estructura de la Tabla
// Puedes empezar con datos predefinidos para un grupo.
const equiposIniciales = [
    { nombre: "Leones FC", logo: "logo1.png", grupo: "A" },
    { nombre: "Águilas Rojas", logo: "logo2.png", grupo: "A" },
    { nombre: "Tigres Azules", logo: "logo3.png", grupo: "A" },
    { nombre: "Halcones Dorados", logo: "logo4.png", grupo: "A" }
];

// Estructura para almacenar las estadísticas de cada equipo
let tabla = {}; 
let resultados = []; // Almacena todos los resultados ingresados

// 2. Inicializar la Tabla con Equipos
function inicializarTabla(equipos) {
    tabla = {};
    equipos.forEach(equipo => {
        tabla[equipo.nombre] = {
            nombre: equipo.nombre,
            ptos: 0,
            pj: 0,
            pg: 0,
            pe: 0,
            pp: 0,
            gf: 0,
            gc: 0,
            dg: 0,
            // Aquí puedes agregar la URL del logo si es necesario
        };
    });
}

// 3. Función Central: Calcular y Actualizar la Tabla
function recalcularTabla() {
    // 1. Reiniciar estadísticas
    inicializarTabla(equiposIniciales);

    // 2. Procesar cada resultado registrado
    resultados.forEach(res => {
        const equipo1 = tabla[res.equipo1];
        const equipo2 = tabla[res.equipo2];
        const g1 = res.goles1;
        const g2 = res.goles2;

        // A. Actualizar Partidos Jugados (PJ)
        equipo1.pj++;
        equipo2.pj++;

        // B. Actualizar Goles (GF y GC)
        equipo1.gf += g1;
        equipo1.gc += g2;
        equipo2.gf += g2;
        equipo2.gc += g1;

        // C. Determinar Resultado y Puntos
        if (g1 > g2) {
            // Gana Equipo 1
            equipo1.ptos += 3;
            equipo1.pg++;
            equipo2.pp++;
        } else if (g2 > g1) {
            // Gana Equipo 2
            equipo2.ptos += 3;
            equipo2.pg++;
            equipo1.pp++;
        } else {
            // Empate
            equipo1.ptos += 1;
            equipo2.ptos += 1;
            equipo1.pe++;
            equipo2.pe++;
        }

        // D. Actualizar Diferencia de Goles (DG)
        equipo1.dg = equipo1.gf - equipo1.gc;
        equipo2.dg = equipo2.gf - equipo2.gc;
    });

    // 3. Mostrar la Tabla en el HTML
    mostrarTabla();
}

// 4. Función para dibujar la Tabla en el HTML
function mostrarTabla() {
    const tbody = document.querySelector('#tabla-grupo-a tbody');
    tbody.innerHTML = ''; // Limpiar tabla anterior

    // Convertir el objeto 'tabla' a un array para poder ordenarlo
    let equiposOrdenados = Object.values(tabla);

    // Criterios de ordenación: 
    // 1. Puntos (Ptos)
    // 2. Diferencia de Goles (DG)
    // 3. Goles a Favor (GF)
    equiposOrdenados.sort((a, b) => {
        if (b.ptos !== a.ptos) {
            return b.ptos - a.ptos; // Mayor Ptos primero
        }
        if (b.dg !== a.dg) {
            return b.dg - a.dg; // Mayor DG primero
        }
        return b.gf - a.gf; // Mayor GF primero
    });

    equiposOrdenados.forEach(equipo => {
        const row = tbody.insertRow();
        row.insertCell().textContent = equipo.nombre;
        row.insertCell().textContent = equipo.ptos;
        row.insertCell().textContent = equipo.pj;
        row.insertCell().textContent = equipo.pg;
        row.insertCell().textContent = equipo.pe;
        row.insertCell().textContent = equipo.pp;
        row.insertCell().textContent = equipo.gf;
        row.insertCell().textContent = equipo.gc;
        row.insertCell().textContent = equipo.dg;
    });
}

// 5. Gestión del Formulario de Ingreso de Resultados
const formResultado = document.getElementById('form-resultado');

formResultado.addEventListener('submit', function(e) {
    e.preventDefault(); // Evitar recarga de página

    const equipo1 = document.getElementById('equipo1').value;
    const goles1 = parseInt(document.getElementById('goles1').value);
    const equipo2 = document.getElementById('equipo2').value;
    const goles2 = parseInt(document.getElementById('goles2').value);

    if (equipo1 === equipo2) {
        alert("Los equipos no pueden ser el mismo.");
        return;
    }

    // Guardar el nuevo resultado
    resultados.push({ equipo1, goles1, equipo2, goles2 });

    // Recalcular y mostrar la tabla
    recalcularTabla();

    // Opcional: limpiar el formulario
    formResultado.reset();
});

// 6. Rellenar los Selects de Equipos
function llenarSelects(equipos) {
    const select1 = document.getElementById('equipo1');
    const select2 = document.getElementById('equipo2');

    equipos.forEach(equipo => {
        const option1 = document.createElement('option');
        option1.value = equipo.nombre;
        option1.textContent = equipo.nombre;
        select1.appendChild(option1);

        const option2 = document.createElement('option');
        option2.value = equipo.nombre;
        option2.textContent = equipo.nombre;
        select2.appendChild(option2);
    });
}

// Inicializar la aplicación al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    inicializarTabla(equiposIniciales);
    llenarSelects(equiposIniciales);
    // Mostrar la tabla vacía inicialmente
    mostrarTabla(); 
});

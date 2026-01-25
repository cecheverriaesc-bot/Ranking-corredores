import { CorredorData, HistoryData, TeamConfig } from './types';

export const MONTHLY_GOAL = 1928;

export interface DailyStat { date: string; coord: string; count: number; }
export const DAILY_STATS: DailyStat[] = [
    {
        "date": "2026-01-01",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-01",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 5
    },
    {
        "date": "2026-01-01",
        "coord": "luis.gomez@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-02",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 9
    },
    {
        "date": "2026-01-02",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 17
    },
    {
        "date": "2026-01-02",
        "coord": "luis.gomez@assetplan.cl",
        "count": 17
    },
    {
        "date": "2026-01-02",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-03",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 11
    },
    {
        "date": "2026-01-03",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 14
    },
    {
        "date": "2026-01-03",
        "coord": "luis.gomez@assetplan.cl",
        "count": 10
    },
    {
        "date": "2026-01-03",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-04",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 8
    },
    {
        "date": "2026-01-04",
        "coord": "luis.gomez@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-04",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-05",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 13
    },
    {
        "date": "2026-01-05",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 43
    },
    {
        "date": "2026-01-05",
        "coord": "luis.gomez@assetplan.cl",
        "count": 24
    },
    {
        "date": "2026-01-05",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-06",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 11
    },
    {
        "date": "2026-01-06",
        "coord": "angely.rojo@assetplan.cl",
        "count": 3
    },
    {
        "date": "2026-01-06",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 42
    },
    {
        "date": "2026-01-06",
        "coord": "luis.gomez@assetplan.cl",
        "count": 34
    },
    {
        "date": "2026-01-06",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 4
    },
    {
        "date": "2026-01-07",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 15
    },
    {
        "date": "2026-01-07",
        "coord": "angely.rojo@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-07",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 40
    },
    {
        "date": "2026-01-07",
        "coord": "luis.gomez@assetplan.cl",
        "count": 37
    },
    {
        "date": "2026-01-07",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 3
    },
    {
        "date": "2026-01-08",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 13
    },
    {
        "date": "2026-01-08",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 25
    },
    {
        "date": "2026-01-08",
        "coord": "luis.gomez@assetplan.cl",
        "count": 17
    },
    {
        "date": "2026-01-08",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-09",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 14
    },
    {
        "date": "2026-01-09",
        "coord": "angely.rojo@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-09",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 51
    },
    {
        "date": "2026-01-09",
        "coord": "luis.gomez@assetplan.cl",
        "count": 27
    },
    {
        "date": "2026-01-09",
        "coord": "maria.chacin@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-09",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-10",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 6
    },
    {
        "date": "2026-01-10",
        "coord": "angely.rojo@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-10",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 24
    },
    {
        "date": "2026-01-10",
        "coord": "luis.gomez@assetplan.cl",
        "count": 14
    },
    {
        "date": "2026-01-10",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-11",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-11",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 10
    },
    {
        "date": "2026-01-11",
        "coord": "luis.gomez@assetplan.cl",
        "count": 7
    },
    {
        "date": "2026-01-11",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-12",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 9
    },
    {
        "date": "2026-01-12",
        "coord": "angely.rojo@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-12",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 35
    },
    {
        "date": "2026-01-12",
        "coord": "luis.gomez@assetplan.cl",
        "count": 17
    },
    {
        "date": "2026-01-12",
        "coord": "maria.chacin@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-12",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 6
    },
    {
        "date": "2026-01-13",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 14
    },
    {
        "date": "2026-01-13",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 39
    },
    {
        "date": "2026-01-13",
        "coord": "luis.gomez@assetplan.cl",
        "count": 25
    },
    {
        "date": "2026-01-13",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 5
    },
    {
        "date": "2026-01-14",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 9
    },
    {
        "date": "2026-01-14",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 44
    },
    {
        "date": "2026-01-14",
        "coord": "luis.gomez@assetplan.cl",
        "count": 23
    },
    {
        "date": "2026-01-14",
        "coord": "maria.chacin@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-14",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 4
    },
    {
        "date": "2026-01-15",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 10
    },
    {
        "date": "2026-01-15",
        "coord": "angely.rojo@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-15",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 26
    },
    {
        "date": "2026-01-15",
        "coord": "luis.gomez@assetplan.cl",
        "count": 36
    },
    {
        "date": "2026-01-15",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 8
    },
    {
        "date": "2026-01-16",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 11
    },
    {
        "date": "2026-01-16",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 36
    },
    {
        "date": "2026-01-16",
        "coord": "luis.gomez@assetplan.cl",
        "count": 21
    },
    {
        "date": "2026-01-16",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-17",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 6
    },
    {
        "date": "2026-01-17",
        "coord": "angely.rojo@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-17",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 25
    },
    {
        "date": "2026-01-17",
        "coord": "luis.gomez@assetplan.cl",
        "count": 17
    },
    {
        "date": "2026-01-17",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 3
    },
    {
        "date": "2026-01-18",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 3
    },
    {
        "date": "2026-01-18",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 6
    },
    {
        "date": "2026-01-18",
        "coord": "luis.gomez@assetplan.cl",
        "count": 4
    },
    {
        "date": "2026-01-18",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-19",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 5
    },
    {
        "date": "2026-01-19",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 36
    },
    {
        "date": "2026-01-19",
        "coord": "luis.gomez@assetplan.cl",
        "count": 30
    },
    {
        "date": "2026-01-19",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 6
    },
    {
        "date": "2026-01-20",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 7
    },
    {
        "date": "2026-01-20",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 38
    },
    {
        "date": "2026-01-20",
        "coord": "luis.gomez@assetplan.cl",
        "count": 31
    },
    {
        "date": "2026-01-20",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 5
    },
    {
        "date": "2026-01-21",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 10
    },
    {
        "date": "2026-01-21",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 41
    },
    {
        "date": "2026-01-21",
        "coord": "luis.gomez@assetplan.cl",
        "count": 23
    },
    {
        "date": "2026-01-21",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 7
    },
    {
        "date": "2026-01-22",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 12
    },
    {
        "date": "2026-01-22",
        "coord": "angely.rojo@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-22",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 37
    },
    {
        "date": "2026-01-22",
        "coord": "luis.gomez@assetplan.cl",
        "count": 31
    },
    {
        "date": "2026-01-22",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-23",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 9
    },
    {
        "date": "2026-01-23",
        "coord": "angely.rojo@assetplan.cl",
        "count": 2
    },
    {
        "date": "2026-01-23",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 53
    },
    {
        "date": "2026-01-23",
        "coord": "luis.gomez@assetplan.cl",
        "count": 27
    },
    {
        "date": "2026-01-23",
        "coord": "maria.chacin@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-23",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 4
    },
    {
        "date": "2026-01-24",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 1
    },
    {
        "date": "2026-01-24",
        "coord": "carlos.echeverria@assetplan.cl",
        "count": 33
    },
    {
        "date": "2026-01-24",
        "coord": "luis.gomez@assetplan.cl",
        "count": 19
    },
    {
        "date": "2026-01-24",
        "coord": "nataly.espinoza@assetplan.cl",
        "count": 2
    }
];

// ============================================================================
// OTROS CORREDORES (Institucionales / No RM / Switch) - GENERATED DYNAMICALLY
// ============================================================================
export const OTHER_BROKERS_2026: CorredorData[] = [
    {
        "name": "Henry Colina (Rumirent)",
        "val": 39,
        "fallen": 0,
        "leads": 298,
        "agendas": 56,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Vivao (Nicole Jones)",
        "val": 38,
        "fallen": 0,
        "leads": 116,
        "agendas": 4,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Arriendos Kodu",
        "val": 26,
        "fallen": 0,
        "leads": 40,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Confianza Inmobiliaria (Raul Mena)",
        "val": 20,
        "fallen": 0,
        "leads": 119,
        "agendas": 74,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Corredor Switch",
        "val": 9,
        "fallen": 0,
        "leads": 11,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Plaza & Nieto (Gloria Nieto)",
        "val": 8,
        "fallen": 0,
        "leads": 20,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Camila Fuenzalida",
        "val": 7,
        "fallen": 0,
        "leads": 64,
        "agendas": 7,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Legacy Business",
        "val": 6,
        "fallen": 0,
        "leads": 10,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Alejandra Romo",
        "val": 2,
        "fallen": 0,
        "leads": 4,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Rosa Gana",
        "val": 2,
        "fallen": 0,
        "leads": 67,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Inversion Total",
        "val": 2,
        "fallen": 0,
        "leads": 57,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Ok Rent (Andrea Ferrer)",
        "val": 2,
        "fallen": 0,
        "leads": 52,
        "agendas": 6,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Corredor Switch 1 Switch",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Ernesto Moscoso",
        "val": 0,
        "fallen": 0,
        "leads": 1,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Alberto Del Campo",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Gloria Cecilia Salamanca Bruner",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Xiomara Yepez",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    }
];

// ============================================================================
// RANKING ENERO 2026 - GENERATED DYNAMICALLY
// ============================================================================
export const CURRENT_RANKING_2026: CorredorData[] = [
    {
        "name": "Rosangela Cirelli",
        "val": 53,
        "fallen": 1,
        "leads": 205,
        "agendas": 65,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Isadora Zepeda",
        "val": 36,
        "fallen": 2,
        "leads": 87,
        "agendas": 27,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Johanna Hernandez",
        "val": 34,
        "fallen": 0,
        "leads": 166,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Henry Rodriguez",
        "val": 28,
        "fallen": 1,
        "leads": 285,
        "agendas": 42,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yessica Asuaje",
        "val": 24,
        "fallen": 1,
        "leads": 106,
        "agendas": 56,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Dutglas Delmoral",
        "val": 23,
        "fallen": 2,
        "leads": 79,
        "agendas": 1,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Adriana Ollarves",
        "val": 23,
        "fallen": 0,
        "leads": 232,
        "agendas": 37,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Paola Malave",
        "val": 23,
        "fallen": 0,
        "leads": 47,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Elkis Daza",
        "val": 21,
        "fallen": 1,
        "leads": 103,
        "agendas": 54,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Annhelys Cardiet",
        "val": 21,
        "fallen": 0,
        "leads": 242,
        "agendas": 30,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Mayerling Soto",
        "val": 19,
        "fallen": 1,
        "leads": 99,
        "agendas": 30,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yonathan Pino",
        "val": 19,
        "fallen": 0,
        "leads": 97,
        "agendas": 62,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Dennys Morales",
        "val": 19,
        "fallen": 1,
        "leads": 243,
        "agendas": 65,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Nailet Rojo",
        "val": 19,
        "fallen": 1,
        "leads": 256,
        "agendas": 64,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Luis Pernalete",
        "val": 18,
        "fallen": 0,
        "leads": 124,
        "agendas": 51,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Carla Palma",
        "val": 17,
        "fallen": 0,
        "leads": 96,
        "agendas": 34,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Carlos Zambrano",
        "val": 17,
        "fallen": 1,
        "leads": 100,
        "agendas": 8,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Daniela Maritza Portillo Trompiz",
        "val": 17,
        "fallen": 1,
        "leads": 267,
        "agendas": 21,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yexica Gomez",
        "val": 16,
        "fallen": 0,
        "leads": 111,
        "agendas": 38,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Victoria D\u00edaz",
        "val": 16,
        "fallen": 2,
        "leads": 149,
        "agendas": 28,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yanelaine Reyes",
        "val": 16,
        "fallen": 0,
        "leads": 160,
        "agendas": 45,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Sofia Bravo",
        "val": 16,
        "fallen": 0,
        "leads": 126,
        "agendas": 54,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Christian Subiabre",
        "val": 15,
        "fallen": 0,
        "leads": 238,
        "agendas": 51,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Daina Tapia",
        "val": 15,
        "fallen": 1,
        "leads": 86,
        "agendas": 15,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Angela Palomo",
        "val": 15,
        "fallen": 0,
        "leads": 45,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Enihet Curpa",
        "val": 15,
        "fallen": 0,
        "leads": 159,
        "agendas": 21,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yinglis Hernandez",
        "val": 15,
        "fallen": 0,
        "leads": 149,
        "agendas": 36,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yerimar Portillo",
        "val": 13,
        "fallen": 1,
        "leads": 38,
        "agendas": 1,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Dania Chirinos",
        "val": 13,
        "fallen": 1,
        "leads": 158,
        "agendas": 3,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Erika Cepeda",
        "val": 13,
        "fallen": 1,
        "leads": 102,
        "agendas": 24,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Ingrid Mu\u00f1oz",
        "val": 13,
        "fallen": 0,
        "leads": 78,
        "agendas": 16,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Marklim Javier Gonz\u00e1lez Arria",
        "val": 13,
        "fallen": 0,
        "leads": 145,
        "agendas": 30,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Maritza Faundez",
        "val": 12,
        "fallen": 1,
        "leads": 176,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Gustavo Gonzalez",
        "val": 11,
        "fallen": 0,
        "leads": 155,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Daniel Alfredo Devita Le\u00f3n",
        "val": 11,
        "fallen": 0,
        "leads": 110,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Daniela Paola Magrini",
        "val": 11,
        "fallen": 0,
        "leads": 90,
        "agendas": 13,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Paul Perdomo",
        "val": 11,
        "fallen": 0,
        "leads": 73,
        "agendas": 50,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Ana Flores",
        "val": 11,
        "fallen": 0,
        "leads": 131,
        "agendas": 24,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Karla Garcia",
        "val": 10,
        "fallen": 1,
        "leads": 62,
        "agendas": 6,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Marlyn Parra",
        "val": 10,
        "fallen": 0,
        "leads": 95,
        "agendas": 33,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Rosanyelys Cordova",
        "val": 10,
        "fallen": 0,
        "leads": 180,
        "agendas": 34,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Julio C\u00e9sar Marcano Giuliani",
        "val": 10,
        "fallen": 0,
        "leads": 94,
        "agendas": 15,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Gabriela Margoth D\u00edaz G\u00f3mez",
        "val": 10,
        "fallen": 0,
        "leads": 63,
        "agendas": 3,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Lorena Son Rangel",
        "val": 10,
        "fallen": 1,
        "leads": 113,
        "agendas": 18,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Valeska Chavez",
        "val": 9,
        "fallen": 1,
        "leads": 107,
        "agendas": 20,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Marco Martinez",
        "val": 9,
        "fallen": 0,
        "leads": 37,
        "agendas": 11,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Giovanny Gutierrez",
        "val": 9,
        "fallen": 0,
        "leads": 76,
        "agendas": 8,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Hugo Sebasti\u00e1n Gonz\u00e1lez Vel\u00e1squez",
        "val": 9,
        "fallen": 0,
        "leads": 103,
        "agendas": 10,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Alexander Pereira",
        "val": 8,
        "fallen": 1,
        "leads": 28,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Esthefani Gonzalez",
        "val": 8,
        "fallen": 0,
        "leads": 62,
        "agendas": 15,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yolimar Aguilar",
        "val": 8,
        "fallen": 0,
        "leads": 65,
        "agendas": 23,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Carolina Rosales",
        "val": 8,
        "fallen": 0,
        "leads": 44,
        "agendas": 16,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Mar\u00eda Andreina P\u00e9rez Guerrero",
        "val": 8,
        "fallen": 0,
        "leads": 248,
        "agendas": 52,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Elisa Torres",
        "val": 8,
        "fallen": 0,
        "leads": 145,
        "agendas": 19,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Kelly Alexandra V\u00e1squez Narvaez",
        "val": 8,
        "fallen": 0,
        "leads": 173,
        "agendas": 11,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Susana Fabiola S\u00e1nchez Hern\u00e1ndez",
        "val": 8,
        "fallen": 0,
        "leads": 83,
        "agendas": 26,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Francisco Gonzalez",
        "val": 7,
        "fallen": 0,
        "leads": 129,
        "agendas": 8,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Ivon Urra",
        "val": 7,
        "fallen": 0,
        "leads": 72,
        "agendas": 13,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Nelly Ocando",
        "val": 7,
        "fallen": 0,
        "leads": 60,
        "agendas": 24,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yanioscar Margarita Nu\u00f1ez Sarramera",
        "val": 7,
        "fallen": 0,
        "leads": 57,
        "agendas": 18,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Santiago Fuentes",
        "val": 7,
        "fallen": 0,
        "leads": 166,
        "agendas": 32,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Maryse Arria",
        "val": 7,
        "fallen": 0,
        "leads": 70,
        "agendas": 11,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Jean Patricio Roa",
        "val": 7,
        "fallen": 0,
        "leads": 77,
        "agendas": 4,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Sarah Volcanes",
        "val": 7,
        "fallen": 0,
        "leads": 77,
        "agendas": 15,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yealvanny Perez",
        "val": 7,
        "fallen": 0,
        "leads": 67,
        "agendas": 8,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Sahmar Jaimes Fuentes",
        "val": 7,
        "fallen": 0,
        "leads": 111,
        "agendas": 21,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "M\u00e1ximo Humberto P\u00e9rez Gonz\u00e1lez",
        "val": 7,
        "fallen": 0,
        "leads": 55,
        "agendas": 39,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Patricia Gonzalez",
        "val": 6,
        "fallen": 0,
        "leads": 58,
        "agendas": 9,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Daiana Quintero",
        "val": 6,
        "fallen": 0,
        "leads": 27,
        "agendas": 7,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Enmanuel Guerrero",
        "val": 6,
        "fallen": 0,
        "leads": 19,
        "agendas": 1,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Alejandra Beatriz Garc\u00eda Miranda",
        "val": 6,
        "fallen": 0,
        "leads": 58,
        "agendas": 7,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Anyalila Franquiz",
        "val": 6,
        "fallen": 0,
        "leads": 18,
        "agendas": 1,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Ruth Mary Mata Martinez",
        "val": 6,
        "fallen": 0,
        "leads": 66,
        "agendas": 2,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Lesbia Utrilla",
        "val": 5,
        "fallen": 0,
        "leads": 28,
        "agendas": 1,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Daniela Cordero",
        "val": 5,
        "fallen": 0,
        "leads": 58,
        "agendas": 2,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Henmilys Medina",
        "val": 5,
        "fallen": 0,
        "leads": 15,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Felix Ferrer",
        "val": 5,
        "fallen": 0,
        "leads": 164,
        "agendas": 11,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Luisana Albarez",
        "val": 5,
        "fallen": 0,
        "leads": 62,
        "agendas": 11,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Emeric Bergstrom Ibarra",
        "val": 5,
        "fallen": 0,
        "leads": 161,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yenny Alejandra D\u00edaz Vald\u00e9s",
        "val": 5,
        "fallen": 0,
        "leads": 191,
        "agendas": 11,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Wendy Navarro",
        "val": 5,
        "fallen": 0,
        "leads": 61,
        "agendas": 14,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Patricia Latorre",
        "val": 5,
        "fallen": 0,
        "leads": 37,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Jorge Escobar",
        "val": 5,
        "fallen": 0,
        "leads": 33,
        "agendas": 6,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Andrea Carolina Soto Inzunza",
        "val": 5,
        "fallen": 0,
        "leads": 33,
        "agendas": 4,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Luisangela Morales De Garc\u00eda",
        "val": 5,
        "fallen": 0,
        "leads": 95,
        "agendas": 30,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Romelean Lopez",
        "val": 4,
        "fallen": 0,
        "leads": 25,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Melida Casta\u00f1eda",
        "val": 4,
        "fallen": 0,
        "leads": 50,
        "agendas": 3,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Alejandro Rodriguez",
        "val": 4,
        "fallen": 0,
        "leads": 35,
        "agendas": 13,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Aillien Rojas",
        "val": 4,
        "fallen": 0,
        "leads": 61,
        "agendas": 9,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yeni Isabel Mar\u00edn D\u00edaz",
        "val": 4,
        "fallen": 1,
        "leads": 32,
        "agendas": 11,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Paul Andr\u00e9s Gonz\u00e1lez Cerda",
        "val": 4,
        "fallen": 0,
        "leads": 53,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Diego Antonio Varas Lira",
        "val": 4,
        "fallen": 0,
        "leads": 10,
        "agendas": 6,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Desiree Hern\u00e1ndez Nieto",
        "val": 4,
        "fallen": 0,
        "leads": 85,
        "agendas": 20,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Edmary Dauvinett Bolivar Hern\u00e1ndez",
        "val": 4,
        "fallen": 0,
        "leads": 180,
        "agendas": 9,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Jennyfer Portillo",
        "val": 3,
        "fallen": 1,
        "leads": 18,
        "agendas": 1,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Eugenio Arrevilla",
        "val": 3,
        "fallen": 0,
        "leads": 7,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Carlos Gonzalez",
        "val": 3,
        "fallen": 0,
        "leads": 34,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Andreina Carolina L\u00f3pez Pedrique",
        "val": 3,
        "fallen": 0,
        "leads": 16,
        "agendas": 10,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Valeria Carolina Navarro Mondaca",
        "val": 3,
        "fallen": 0,
        "leads": 102,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Luimar Marilin Sucre Jim\u00e9nez",
        "val": 3,
        "fallen": 0,
        "leads": 124,
        "agendas": 7,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yenkly Karelys Le\u00f3n Pereira",
        "val": 3,
        "fallen": 0,
        "leads": 83,
        "agendas": 4,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yhoselyn Jose Vel\u00e1squez Hern\u00e1ndez",
        "val": 3,
        "fallen": 0,
        "leads": 30,
        "agendas": 3,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Sebastian Pirela",
        "val": 3,
        "fallen": 0,
        "leads": 62,
        "agendas": 12,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Karen Lesmes",
        "val": 2,
        "fallen": 0,
        "leads": 21,
        "agendas": 5,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Joenny Moncada",
        "val": 2,
        "fallen": 0,
        "leads": 21,
        "agendas": 1,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Hector Cardiet",
        "val": 2,
        "fallen": 0,
        "leads": 39,
        "agendas": 2,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Ana Mar\u00eda Pernia Vivas",
        "val": 2,
        "fallen": 0,
        "leads": 23,
        "agendas": 1,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Auribel Landaeta",
        "val": 2,
        "fallen": 0,
        "leads": 27,
        "agendas": 4,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Yoanetzy Rodriguez",
        "val": 2,
        "fallen": 0,
        "leads": 41,
        "agendas": 5,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Nathalie Del Valle Guariman Lima",
        "val": 2,
        "fallen": 1,
        "leads": 29,
        "agendas": 4,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Osclari Andreina Fiorino Saavedra",
        "val": 2,
        "fallen": 0,
        "leads": 33,
        "agendas": 3,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Jeanette Mendoza",
        "val": 1,
        "fallen": 0,
        "leads": 2,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Mar\u00eda Elena Katny",
        "val": 1,
        "fallen": 0,
        "leads": 78,
        "agendas": 4,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Juan Uribe",
        "val": 1,
        "fallen": 0,
        "leads": 20,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Joselin Quintero",
        "val": 1,
        "fallen": 0,
        "leads": 28,
        "agendas": 2,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Maryelis Lugo",
        "val": 1,
        "fallen": 2,
        "leads": 37,
        "agendas": 7,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Veronica Saumell",
        "val": 1,
        "fallen": 0,
        "leads": 5,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Marian Escarate",
        "val": 1,
        "fallen": 0,
        "leads": 88,
        "agendas": 3,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Natalia Alvarado",
        "val": 1,
        "fallen": 0,
        "leads": 41,
        "agendas": 2,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Claudia Valenzuela",
        "val": 1,
        "fallen": 0,
        "leads": 17,
        "agendas": 1,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Madeleine Margot C\u00e9spedes Le\u00f3n",
        "val": 1,
        "fallen": 0,
        "leads": 2,
        "agendas": 3,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Virginia Del Valle Guerra Marin",
        "val": 1,
        "fallen": 0,
        "leads": 8,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Yenisleidys Fern\u00e1ndez Guerrero",
        "val": 1,
        "fallen": 0,
        "leads": 9,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Grachi Carolina Cabriles Ampiez",
        "val": 1,
        "fallen": 0,
        "leads": 30,
        "agendas": 11,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Ysela Esther Fiorino Saavedra",
        "val": 1,
        "fallen": 0,
        "leads": 5,
        "agendas": 3,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Michelle Pino",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Diego Andrade",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Francisca Camila Cabero Gornall",
        "val": 0,
        "fallen": 0,
        "leads": 3,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Manuel Duran",
        "val": 0,
        "fallen": 0,
        "leads": 2,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Mario Lepore",
        "val": 0,
        "fallen": 0,
        "leads": 10,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Douglas Rojo",
        "val": 0,
        "fallen": 0,
        "leads": 10,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "David Berrueta",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Jorge A\u00f1ez",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Jessica Miranda",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Manuel Martinez",
        "val": 0,
        "fallen": 0,
        "leads": 1,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Dominic Berna",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Cristian Uribe",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Ver\u00f3nica Gonz\u00e1lez",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Kristhy Guzman",
        "val": 0,
        "fallen": 0,
        "leads": 17,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Nataly Espinoza",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Catalina Salvo Rojas",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Francisca Vidal Gajardo",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Yelitza Andrea Perdomo Ocampo",
        "val": 0,
        "fallen": 0,
        "leads": 39,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    },
    {
        "name": "Willie Moncada",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Paola Nazareth Rodr\u00edguez Barrios",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Yeissi Mu\u00f1oz",
        "val": 0,
        "fallen": 0,
        "leads": 1,
        "agendas": 0,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Claudia Valdes",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Gerardo Cabrera",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Angelica Robles",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Claudia Mu\u00f1oz",
        "val": 0,
        "fallen": 0,
        "leads": 14,
        "agendas": 1,
        "coord": "luis.gomez@assetplan.cl"
    },
    {
        "name": "Mar\u00eda Nuncia Maestre P\u00e9rez",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Cesar Salazar",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Danielis Chacin",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Leandro Osorio Loaiza",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Daniela Sulbaran",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "maria.chacin@assetplan.cl"
    },
    {
        "name": "Ninoska Dusan Miranda Ortega",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Maritza Josefina Cartagena Galindez",
        "val": 0,
        "fallen": 0,
        "leads": 32,
        "agendas": 4,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Yetsabel Colina",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Marisa Irene Cabral",
        "val": 0,
        "fallen": 0,
        "leads": 1,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Fernanda Trinidad Gonz\u00e1lez Abarca",
        "val": 0,
        "fallen": 0,
        "leads": 31,
        "agendas": 4,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Enrique Javier Baeza Solsona",
        "val": 0,
        "fallen": 0,
        "leads": 5,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Marisella Giovanna Flores Burotto",
        "val": 0,
        "fallen": 0,
        "leads": 7,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Michelle Alvarado",
        "val": 0,
        "fallen": 0,
        "leads": 5,
        "agendas": 0,
        "coord": "angely.rojo@assetplan.cl"
    },
    {
        "name": "Ignacio Bustos",
        "val": 0,
        "fallen": 0,
        "leads": 51,
        "agendas": 0,
        "coord": "nataly.espinoza@assetplan.cl"
    },
    {
        "name": "Leonardo Pablo Venegas Jara",
        "val": 0,
        "fallen": 0,
        "leads": 0,
        "agendas": 0,
        "coord": "carlos.echeverria@assetplan.cl"
    }
];

// Curated Agenda Members (Filtered by active status in DB)
export const NAMES_WITH_AGENDA: string[] = [
    "Erika Cepeda",
    "Henry Rodriguez",
    "Luis Pernalete",
    "Mayerling Soto",
    "Nailet Rojo",
    "Paul Perdomo",
    "Rosangela Cirelli",
    "Sofia Bravo",
    "Victoria D\u00edaz",
    "Yanelaine Reyes",
    "Yessica Asuaje",
    "Yexica Gomez",
    "Yinglis Hernandez",
    "Yonathan Pino"
];

// Historical Data Jan 2025
export const HISTORY_2025: Record<string, HistoryData> = {
    "Johana G\u00f3mez": {
        "c": 6,
        "t": 7
    },
    "Diego Andrade": {
        "c": 4,
        "t": 5
    },
    "Melida Casta\u00f1eda": {
        "c": 9,
        "t": 10
    },
    "Ivon Urra": {
        "c": 3,
        "t": 3
    },
    "Benjamin Marcano": {
        "c": 0,
        "t": 3
    },
    "Karen Lesmes": {
        "c": 2,
        "t": 2
    },
    "Hector Cardiet": {
        "c": 12,
        "t": 17
    },
    "Cristian Uribe": {
        "c": 3,
        "t": 4
    },
    "Douglas Rojo": {
        "c": 21,
        "t": 25
    },
    "Emeric Bergstrom Ibarra": {
        "c": 2,
        "t": 7
    },
    "Alexander Pereira": {
        "c": 2,
        "t": 3
    },
    "Maria Morales": {
        "c": 11,
        "t": 14
    },
    "Jeanette Mendoza": {
        "c": 2,
        "t": 3
    },
    "Maryelis Lugo": {
        "c": 1,
        "t": 4
    },
    "Constanza Moya": {
        "c": 1,
        "t": 1
    },
    "Gabriela Quintero": {
        "c": 19,
        "t": 19
    },
    "Jonathan Alfredo Lagos Licancura": {
        "c": 7,
        "t": 9
    },
    "Yinglis Hernandez": {
        "c": 34,
        "t": 39
    },
    "Giovanny Gutierrez": {
        "c": 8,
        "t": 12
    },
    "Evelyn Carolina D\u00edaz Galaz": {
        "c": 0,
        "t": 2
    },
    "Ingrid Mu\u00f1oz": {
        "c": 13,
        "t": 17
    },
    "Michelle Pino": {
        "c": 1,
        "t": 1
    },
    "Rosangela Cirelli": {
        "c": 42,
        "t": 54
    },
    "Francisco Gonzalez": {
        "c": 2,
        "t": 2
    },
    "Isadora Zepeda": {
        "c": 26,
        "t": 35
    },
    "Mar\u00eda Elena Katny": {
        "c": 2,
        "t": 3
    },
    "Alvaro Quintero": {
        "c": 0,
        "t": 5
    },
    "Angela Palomo": {
        "c": 6,
        "t": 9
    },
    "Marco Martinez": {
        "c": 9,
        "t": 10
    },
    "Paul Perdomo": {
        "c": 17,
        "t": 20
    },
    "Andres Reyes": {
        "c": 1,
        "t": 3
    },
    "Nataly Concha": {
        "c": 10,
        "t": 10
    },
    "Johanna Hernandez": {
        "c": 32,
        "t": 44
    },
    "Annhelys Cardiet": {
        "c": 18,
        "t": 24
    },
    "Daniela Pino": {
        "c": 16,
        "t": 21
    },
    "Diego Loy": {
        "c": 5,
        "t": 5
    },
    "Guillermo Antolinez": {
        "c": 1,
        "t": 3
    },
    "Maria Fernanda Meneses": {
        "c": 1,
        "t": 5
    },
    "Elizabeth Valdes": {
        "c": 18,
        "t": 23
    },
    "Robinson Mellado Mu\u00f1oz": {
        "c": 4,
        "t": 8
    },
    "Jose Roche": {
        "c": 3,
        "t": 3
    },
    "Laura Moizant": {
        "c": 5,
        "t": 7
    },
    "Manuel Silva": {
        "c": 5,
        "t": 8
    },
    "Raquel Rosa Valenzuela Brizuela": {
        "c": 1,
        "t": 1
    },
    "Christian Subiabre": {
        "c": 13,
        "t": 20
    },
    "Enmanuel Guerrero": {
        "c": 1,
        "t": 1
    },
    "Carolina Valenzuela": {
        "c": 0,
        "t": 0
    },
    "Yorcy Tovar": {
        "c": 1,
        "t": 1
    },
    "Marlyn Parra": {
        "c": 12,
        "t": 14
    },
    "Rosa Gana": {
        "c": 2,
        "t": 3
    },
    "Maria Del Pilar Diaz": {
        "c": 1,
        "t": 1
    },
    "Carlos Alvarez": {
        "c": 9,
        "t": 11
    },
    "Joenny Moncada": {
        "c": 17,
        "t": 21
    },
    "Felix Ferrer": {
        "c": 18,
        "t": 25
    },
    "Patricia Gonzalez": {
        "c": 8,
        "t": 10
    },
    "Geraldine Trujillo": {
        "c": 4,
        "t": 4
    },
    "Daina Tapia": {
        "c": 10,
        "t": 16
    },
    "Yasmin Garc\u00eda": {
        "c": 5,
        "t": 12
    },
    "Maryse Arria": {
        "c": 14,
        "t": 23
    },
    "Rita Valiente": {
        "c": 2,
        "t": 2
    },
    "Marina Margarita Ceballos Rojas": {
        "c": 3,
        "t": 5
    },
    "Elkis Daza": {
        "c": 30,
        "t": 33
    },
    "Luisana Albarez": {
        "c": 4,
        "t": 6
    },
    "Ejecutivo Assetplan": {
        "c": 0,
        "t": 2
    },
    "Yexica Gomez": {
        "c": 8,
        "t": 17
    },
    "Valeria Carolina Navarro Mondaca": {
        "c": 4,
        "t": 4
    },
    "Andibet Quintero": {
        "c": 14,
        "t": 15
    },
    "Karla Garcia": {
        "c": 0,
        "t": 2
    },
    "Carlos Oropeza": {
        "c": 1,
        "t": 4
    },
    "Katerin Reyes": {
        "c": 1,
        "t": 1
    },
    "Greiry Rodriguez": {
        "c": 2,
        "t": 2
    },
    "Yessica Asuaje": {
        "c": 11,
        "t": 12
    },
    "Romelean Lopez": {
        "c": 2,
        "t": 2
    },
    "Sinead Vasquez": {
        "c": 1,
        "t": 2
    },
    "Luis Pernalete": {
        "c": 16,
        "t": 17
    },
    "Nelly Ocando": {
        "c": 24,
        "t": 29
    },
    "Virginia Del Carmen Lobo Lobo": {
        "c": 3,
        "t": 4
    },
    "Leslie Mariscal": {
        "c": 11,
        "t": 12
    },
    "Jorge A\u00f1ez": {
        "c": 14,
        "t": 20
    },
    "Mayerling Soto": {
        "c": 24,
        "t": 30
    },
    "Ernesto Moscoso": {
        "c": 1,
        "t": 1
    },
    "Manuel Martinez": {
        "c": 30,
        "t": 39
    },
    "Ximena Leiva": {
        "c": 5,
        "t": 5
    },
    "Yolimar Aguilar": {
        "c": 2,
        "t": 3
    },
    "Daniela Paola Magrini": {
        "c": 36,
        "t": 39
    },
    "Camila Fuenzalida": {
        "c": 1,
        "t": 1
    },
    "Yonathan Pino": {
        "c": 27,
        "t": 31
    },
    "Yanelaine Reyes": {
        "c": 4,
        "t": 4
    },
    "Adriana Ollarves": {
        "c": 15,
        "t": 22
    },
    "Yulenny Bencomo": {
        "c": 17,
        "t": 22
    },
    "Morande Oficinas": {
        "c": 3,
        "t": 4
    },
    "Arlyn Pe\u00f1a": {
        "c": 1,
        "t": 2
    },
    "Henry Colina (Rumirent)": {
        "c": 0,
        "t": 6
    },
    "Gensa Arriendos (Maria Araujo)": {
        "c": 8,
        "t": 11
    },
    "Yuleidy Caraballo": {
        "c": 1,
        "t": 1
    },
    "Plaza & Nieto (Gloria Nieto)": {
        "c": 4,
        "t": 5
    },
    "Carlos Gonzalez": {
        "c": 9,
        "t": 14
    },
    "Eugenio Arrevilla": {
        "c": 5,
        "t": 8
    },
    "Fabian Arenas": {
        "c": 4,
        "t": 4
    },
    "Henry Rodriguez": {
        "c": 33,
        "t": 43
    },
    "Angel Marquez": {
        "c": 28,
        "t": 35
    },
    "Ver\u00f3nica Gonz\u00e1lez": {
        "c": 4,
        "t": 6
    },
    "Victoria D\u00edaz": {
        "c": 8,
        "t": 10
    },
    "Alberto Del Campo": {
        "c": 1,
        "t": 1
    },
    "Mar\u00eda Cristina De La Cuadra": {
        "c": 1,
        "t": 3
    },
    "Miriam Flores": {
        "c": 0,
        "t": 1
    },
    "Yerimar Portillo": {
        "c": 24,
        "t": 32
    },
    "Joselin Quintero": {
        "c": 0,
        "t": 2
    },
    "Mauricio Reyes": {
        "c": 2,
        "t": 2
    },
    "Andr\u00e9s Garcia": {
        "c": 3,
        "t": 4
    },
    "Saynell Patricia Mora Zambrano": {
        "c": 9,
        "t": 11
    },
    "Nelly Coromoto Zambrano": {
        "c": 4,
        "t": 5
    },
    "Alejandro Rodriguez": {
        "c": 15,
        "t": 18
    },
    "Karol Yusty": {
        "c": 7,
        "t": 8
    },
    "Lesbia Utrilla": {
        "c": 6,
        "t": 8
    },
    "Ana Roman": {
        "c": 11,
        "t": 15
    },
    "Kareen Araya": {
        "c": 2,
        "t": 2
    },
    "Kariangel Andrea Silva": {
        "c": 14,
        "t": 20
    },
    "Corredor Switch": {
        "c": 19,
        "t": 25
    },
    "Sofia Bravo": {
        "c": 4,
        "t": 8
    },
    "Ana Flores": {
        "c": 0,
        "t": 1
    },
    "Valeska Chavez": {
        "c": 17,
        "t": 21
    },
    "Jennyfer Portillo": {
        "c": 21,
        "t": 24
    },
    "Carlos Zambrano": {
        "c": 18,
        "t": 22
    },
    "Maritza Faundez": {
        "c": 12,
        "t": 15
    },
    "Gustavo Gonzalez": {
        "c": 29,
        "t": 34
    },
    "Alejandra Romo": {
        "c": 12,
        "t": 15
    },
    "Rodrigo Valderrama": {
        "c": 18,
        "t": 20
    },
    "Andreina Carolina L\u00f3pez Pedrique": {
        "c": 14,
        "t": 19
    },
    "Jairon Dumes": {
        "c": 16,
        "t": 19
    },
    "Mario Lepore": {
        "c": 7,
        "t": 9
    },
    "Dutglas Delmoral": {
        "c": 35,
        "t": 49
    },
    "Dania Chirinos": {
        "c": 20,
        "t": 25
    },
    "Francisca Camila Cabero Gornall": {
        "c": 2,
        "t": 2
    },
    "Nailet Rojo": {
        "c": 3,
        "t": 6
    },
    "Pedro Riveiro": {
        "c": 2,
        "t": 3
    },
    "Pamela Novoa": {
        "c": 1,
        "t": 1
    },
    "Santiago Fuentes": {
        "c": 16,
        "t": 21
    },
    "Daiana Quintero": {
        "c": 20,
        "t": 24
    },
    "Ruben Andr\u00e9s Castro Amaza": {
        "c": 4,
        "t": 7
    },
    "Daniel Alfredo Devita Le\u00f3n": {
        "c": 15,
        "t": 17
    },
    "Cintia Cecilia Moreno Monz\u00f3n": {
        "c": 7,
        "t": 8
    },
    "Esthefani Gonzalez": {
        "c": 17,
        "t": 23
    },
    "Dennys Morales": {
        "c": 21,
        "t": 27
    },
    "Erika Cepeda": {
        "c": 15,
        "t": 23
    },
    "Carla Palma": {
        "c": 2,
        "t": 2
    },
    "Enihet Curpa": {
        "c": 9,
        "t": 12
    },
    "Rosanyelys Cordova": {
        "c": 18,
        "t": 23
    }
};

export const LAST_UPDATE = '24/01/2026 23:22';

export const TEAMS: Record<string, TeamConfig> = {
    "carlos.echeverria@assetplan.cl": { name: "Squad Carlos", icon: "Flame", color: "text-orange-600", bg: "bg-orange-50 border-orange-200", my: false },
    "luis.gomez@assetplan.cl": { name: "Squad Luis", icon: "Droplet", color: "text-blue-500", bg: "bg-blue-50 border-blue-200", my: false },
    "nataly.espinoza@assetplan.cl": { name: "Squad Natu", icon: "GraduationCap", color: "text-indigo-600", bg: "bg-indigo-50 border-indigo-200", my: false },
    "angely.rojo@assetplan.cl": { name: "Squad Angely", icon: "Flower2", color: "text-pink-600", bg: "bg-pink-50 border-pink-200", my: false },
    "maria.chacin@assetplan.cl": { name: "Squad Gabriela", icon: "Star", color: "text-yellow-500", bg: "bg-yellow-50 border-yellow-200", my: false }
};

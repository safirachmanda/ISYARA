/**
 * state_manager.js - Manajemen State Terpusat ISYARA
 * Versi dengan Seed Data dan Fungsi Lengkap
 */

(function(global) {
    'use strict';

    const STORAGE_KEY = 'isyara_dashboard_data';

    // --- Data Default dengan Seed ---
    function getDefaultState() {
        return {
            users: [
                { username: 'superadmin', password: 'admin123', role: 'superadmin', instansi: 'Pusat', status: 'Aktif' },
                { username: 'adm_dinkes', password: 'password123', role: 'admin', instansi: 'Dinas Kesehatan Kota A', status: 'Aktif' },
                { username: 'adm_capil', password: 'password123', role: 'admin', instansi: 'Dinas Capil Kota B', status: 'Aktif' }
            ],
            currentUser: null,
            currentInstansi: 'all',
            eventLog: [],
            insiden: [],
            requests: [],
            problems: [],
            kedb: [],
            qaSimulation: { cloudDown: false, bugUpdate: false },
            notifCounter: 0
        };
    }

    // --- Helper ---
    function generateId(prefix) {
        const now = Date.now().toString(36).toUpperCase();
        const rand = Math.random().toString(36).substring(2,6).toUpperCase();
        return prefix + '-' + now.slice(-4) + rand;
    }

    function formatTime(ts) {
        const d = new Date(ts);
        return d.toLocaleTimeString('id-ID', { hour:'2-digit', minute:'2-digit' });
    }

    function formatDate(ts) {
        const d = new Date(ts);
        return d.toLocaleDateString('id-ID', { day:'2-digit', month:'short', year:'numeric' });
    }

    function filterByInstansi(arr, instansi) {
        if (!arr) return [];
        if (instansi === 'all') return arr;
        return arr.filter(item => item.instansi === instansi || item.instansi === 'Pusat');
    }

    // --- Fungsi untuk Seed Data ---
    function generateSeedData() {
        const now = Date.now();
        const oneHourAgo = now - 3600000;
        const twoHoursAgo = now - 7200000;
        const yesterday = now - 86400000;

        return {
            eventLog: [
                {
                    id: Date.now() + 1,
                    waktu: formatTime(now - 60000),
                    kategori: 'Info',
                    deskripsi: '[LOKET 1] Latensi normal (0.8s)',
                    instansi: 'Dinas Kesehatan Kota A',
                    eskalasi: false
                },
                {
                    id: Date.now() + 2,
                    waktu: formatTime(now - 120000),
                    kategori: 'Warning',
                    deskripsi: '[SERVER] CPU Usage 82%',
                    instansi: 'Pusat',
                    eskalasi: false
                },
                {
                    id: Date.now() + 3,
                    waktu: formatTime(now - 300000),
                    kategori: 'Exception',
                    deskripsi: '[LOKET 3] Kamera gagal inisialisasi',
                    instansi: 'Dinas Kesehatan Kota A',
                    eskalasi: false
                },
                {
                    id: Date.now() + 4,
                    waktu: formatTime(now - 600000),
                    kategori: 'Exception',
                    deskripsi: '[LOKET 2] Deteksi gesture timeout',
                    instansi: 'Dinas Capil Kota B',
                    eskalasi: false
                }
            ],
            insiden: [
                {
                    id: 'INC-1001',
                    judul: 'Kamera Loket 3 Mati Total',
                    prioritas: 'Kritis',
                    status: 'Baru',
                    instansi: 'Dinas Kesehatan Kota A',
                    created: now - 1800000,
                    escalatedToProblem: false,
                    sumber: 'Event Eskalasi'
                },
                {
                    id: 'INC-1002',
                    judul: 'Latensi Deteksi > 2 detik',
                    prioritas: 'Sedang',
                    status: 'Ditangani',
                    instansi: 'Pusat',
                    created: now - 7200000,
                    escalatedToProblem: false,
                    sumber: 'Monitoring Sistem'
                },
                {
                    id: 'INC-1003',
                    judul: 'Speech-to-Text tidak merespon',
                    prioritas: 'Tinggi',
                    status: 'Baru',
                    instansi: 'Dinas Capil Kota B',
                    created: now - 3600000,
                    escalatedToProblem: false,
                    sumber: 'Laporan Web'
                }
            ],
            requests: [
                {
                    id: 'REQ-001',
                    jenis: 'Aktivasi Loket 4 (Dinkes A)',
                    prioritas: 'Sedang',
                    status: 'Menunggu Approval',
                    instansi: 'Dinas Kesehatan Kota A',
                    sumber: 'Admin'
                },
                {
                    id: 'REQ-002',
                    jenis: 'Permintaan Akses Dashboard untuk Staf',
                    prioritas: 'Rendah',
                    status: 'Disetujui',
                    instansi: 'Dinas Capil Kota B',
                    sumber: 'Admin'
                },
                {
                    id: 'REQ-003',
                    jenis: 'Saran: Tambahkan fitur riwayat percakapan',
                    prioritas: 'Rendah',
                    status: 'Menunggu Approval',
                    instansi: 'Pusat',
                    sumber: 'Laporan Web'
                }
            ],
            problems: [
                {
                    id: 'PRB-001',
                    judul: 'Bug Deteksi Gestur (Overfitting pada kata "Maaf")',
                    sumber: 'INC-1002',
                    status: 'RCA Selesai',
                    instansi: 'Pusat'
                }
            ],
            kedb: [
                {
                    kode: 'ERR-01',
                    deskripsi: 'Model AI Overfitting pada huruf "A"',
                    workaround: 'Rollback ke model statis v2.0',
                    statusSolusi: 'Selesai (RFC #022)',
                    sumberProblem: 'PRB-001'
                },
                {
                    kode: 'ERR-02',
                    deskripsi: 'Timeout koneksi kamera pada device tertentu',
                    workaround: 'Restart aplikasi atau gunakan kamera eksternal',
                    statusSolusi: 'Sedang dikaji'
                }
            ]
        };
    }

    // --- State Load/Save ---
    function loadState() {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            const def = getDefaultState();
            // Tambahkan seed data
            const seed = generateSeedData();
            def.eventLog = seed.eventLog;
            def.insiden = seed.insiden;
            def.requests = seed.requests;
            def.problems = seed.problems;
            def.kedb = seed.kedb;
            saveState(def);
            return def;
        }
        try {
            const data = JSON.parse(raw);
            // Migrasi jika ada field baru
            const def = getDefaultState();
            for (let key in def) {
                if (!(key in data)) {
                    data[key] = def[key];
                }
            }
            // Pastikan data seed ada jika kosong
            if (data.eventLog.length === 0 && data.insiden.length === 0) {
                const seed = generateSeedData();
                data.eventLog = seed.eventLog;
                data.insiden = seed.insiden;
                data.requests = seed.requests;
                data.problems = seed.problems;
                data.kedb = seed.kedb;
                saveState(data);
            }
            return data;
        } catch(e) {
            console.warn('Gagal parse state, reset ke default dengan seed.');
            const def = getDefaultState();
            const seed = generateSeedData();
            def.eventLog = seed.eventLog;
            def.insiden = seed.insiden;
            def.requests = seed.requests;
            def.problems = seed.problems;
            def.kedb = seed.kedb;
            saveState(def);
            return def;
        }
    }

    function saveState(state) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    // --- API Publik ---
    const StateManager = {
        // State Dasar
        getState: loadState,
        saveState: saveState,
        resetState: function() {
            const def = getDefaultState();
            const seed = generateSeedData();
            def.eventLog = seed.eventLog;
            def.insiden = seed.insiden;
            def.requests = seed.requests;
            def.problems = seed.problems;
            def.kedb = seed.kedb;
            saveState(def);
            return def;
        },

        // Users
        getUsers: function() {
            const state = loadState();
            return state.users;
        },
        getUser: function(username) {
            const state = loadState();
            return state.users.find(u => u.username === username) || null;
        },
        addUser: function(userData) {
            const state = loadState();
            if (state.users.find(u => u.username === userData.username)) {
                throw new Error('Username sudah terdaftar');
            }
            const newUser = {
                username: userData.username,
                password: userData.password || 'password123',
                role: userData.role || 'admin',
                instansi: userData.instansi || 'Pusat',
                status: 'Aktif'
            };
            state.users.push(newUser);
            saveState(state);
            return newUser;
        },
        updateUser: function(username, updates) {
            const state = loadState();
            const user = state.users.find(u => u.username === username);
            if (!user) throw new Error('User tidak ditemukan');
            Object.assign(user, updates);
            saveState(state);
            return user;
        },
        deleteUser: function(username) {
            const state = loadState();
            if (username === 'superadmin') throw new Error('Tidak bisa menghapus superadmin');
            state.users = state.users.filter(u => u.username !== username);
            saveState(state);
        },

        // Current User
        getCurrentUser: function() {
            const state = loadState();
            return state.currentUser || null;
        },
        setCurrentUser: function(user) {
            const state = loadState();
            state.currentUser = user;
            saveState(state);
        },
        logout: function() {
            const state = loadState();
            state.currentUser = null;
            saveState(state);
        },
        isLoggedIn: function() {
            const state = loadState();
            return state.currentUser !== null;
        },
        isSuperadmin: function() {
            const state = loadState();
            return state.currentUser && state.currentUser.role === 'superadmin';
        },

        // Instansi
        getCurrentInstansi: function() {
            const state = loadState();
            return state.currentInstansi || 'all';
        },
        setCurrentInstansi: function(instansi) {
            const state = loadState();
            state.currentInstansi = instansi;
            saveState(state);
        },

        // Events
        getEvents: function(instansi) {
            const state = loadState();
            const target = instansi || state.currentInstansi || 'all';
            return filterByInstansi(state.eventLog, target);
        },
        getAllEvents: function() {
            const state = loadState();
            return state.eventLog;
        },
        addEvent: function(eventData) {
            const state = loadState();
            const newEvent = {
                id: Date.now(),
                waktu: formatTime(Date.now()),
                kategori: eventData.kategori || 'Info',
                deskripsi: eventData.deskripsi || '',
                instansi: eventData.instansi || 'Pusat',
                eskalasi: false,
                ...eventData
            };
            state.eventLog.push(newEvent);
            saveState(state);
            return newEvent;
        },
        deleteEvent: function(eventId) {
            const state = loadState();
            state.eventLog = state.eventLog.filter(e => e.id !== eventId);
            saveState(state);
        },
        clearEvents: function() {
            const state = loadState();
            state.eventLog = [];
            saveState(state);
        },

        // Insiden
        getInsiden: function(instansi) {
            const state = loadState();
            const target = instansi || state.currentInstansi || 'all';
            return filterByInstansi(state.insiden, target);
        },
        getAllInsiden: function() {
            const state = loadState();
            return state.insiden;
        },
        addInsiden: function(insidenData) {
            const state = loadState();
            const newInc = {
                id: generateId('INC'),
                judul: insidenData.judul || 'Insiden baru',
                prioritas: insidenData.prioritas || 'Sedang',
                status: insidenData.status || 'Baru',
                instansi: insidenData.instansi || 'Pusat',
                created: Date.now(),
                escalatedToProblem: false,
                sumber: insidenData.sumber || 'Sistem',
                ...insidenData
            };
            state.insiden.push(newInc);
            saveState(state);
            return newInc;
        },
        updateInsiden: function(incId, updates) {
            const state = loadState();
            const inc = state.insiden.find(i => i.id === incId);
            if (!inc) throw new Error('Insiden tidak ditemukan');
            Object.assign(inc, updates);
            saveState(state);
            return inc;
        },
        escalateToProblem: function(incId) {
            const state = loadState();
            const inc = state.insiden.find(i => i.id === incId);
            if (!inc) throw new Error('Insiden tidak ditemukan');
            if (inc.escalatedToProblem) throw new Error('Insiden sudah di-eskalasi');
            const newProb = {
                id: generateId('PRB'),
                judul: inc.judul,
                sumber: inc.id,
                status: 'Investigasi',
                instansi: inc.instansi || 'Pusat'
            };
            state.problems.push(newProb);
            inc.escalatedToProblem = true;
            saveState(state);
            return newProb;
        },
        deleteInsiden: function(incId) {
            const state = loadState();
            state.insiden = state.insiden.filter(i => i.id !== incId);
            saveState(state);
        },

        // Requests
        getRequests: function(instansi) {
            const state = loadState();
            const target = instansi || state.currentInstansi || 'all';
            return filterByInstansi(state.requests, target);
        },
        getAllRequests: function() {
            const state = loadState();
            return state.requests;
        },
        addRequest: function(requestData) {
            const state = loadState();
            const newReq = {
                id: generateId('REQ'),
                jenis: requestData.jenis || 'Permintaan baru',
                prioritas: requestData.prioritas || 'Sedang',
                status: requestData.status || 'Menunggu Approval',
                instansi: requestData.instansi || 'Pusat',
                sumber: requestData.sumber || 'Admin',
                ...requestData
            };
            state.requests.push(newReq);
            saveState(state);
            return newReq;
        },
        updateRequest: function(reqId, updates) {
            const state = loadState();
            const req = state.requests.find(r => r.id === reqId);
            if (!req) throw new Error('Request tidak ditemukan');
            Object.assign(req, updates);
            saveState(state);
            return req;
        },
        deleteRequest: function(reqId) {
            const state = loadState();
            state.requests = state.requests.filter(r => r.id !== reqId);
            saveState(state);
        },

        // Problems
        getProblems: function(instansi) {
            const state = loadState();
            const target = instansi || state.currentInstansi || 'all';
            return filterByInstansi(state.problems, target);
        },
        getAllProblems: function() {
            const state = loadState();
            return state.problems;
        },
        addProblem: function(problemData) {
            const state = loadState();
            const newProb = {
                id: generateId('PRB'),
                judul: problemData.judul || 'Problem baru',
                sumber: problemData.sumber || 'Sistem',
                status: problemData.status || 'Investigasi',
                instansi: problemData.instansi || 'Pusat',
                ...problemData
            };
            state.problems.push(newProb);
            saveState(state);
            return newProb;
        },
        updateProblem: function(probId, updates) {
            const state = loadState();
            const prob = state.problems.find(p => p.id === probId);
            if (!prob) throw new Error('Problem tidak ditemukan');
            Object.assign(prob, updates);
            saveState(state);
            return prob;
        },
        moveToKEDB: function(probId) {
            const state = loadState();
            const prob = state.problems.find(p => p.id === probId);
            if (!prob) throw new Error('Problem tidak ditemukan');
            const newKedb = {
                kode: 'ERR-' + String(state.kedb.length + 1).padStart(2, '0'),
                deskripsi: prob.judul,
                workaround: 'Lihat dokumentasi internal',
                statusSolusi: 'Sedang dikaji',
                sumberProblem: prob.id
            };
            state.kedb.push(newKedb);
            state.problems = state.problems.filter(p => p.id !== probId);
            saveState(state);
            return newKedb;
        },
        deleteProblem: function(probId) {
            const state = loadState();
            state.problems = state.problems.filter(p => p.id !== probId);
            saveState(state);
        },

        // KEDB
        getKEDB: function() {
            const state = loadState();
            return state.kedb;
        },
        addKEDB: function(kedbData) {
            const state = loadState();
            const newKedb = {
                kode: 'ERR-' + String(state.kedb.length + 1).padStart(2, '0'),
                deskripsi: kedbData.deskripsi || 'Error baru',
                workaround: kedbData.workaround || 'Belum ada workaround',
                statusSolusi: kedbData.statusSolusi || 'Sedang dikaji',
                ...kedbData
            };
            state.kedb.push(newKedb);
            saveState(state);
            return newKedb;
        },
        deleteKEDB: function(kode) {
            const state = loadState();
            state.kedb = state.kedb.filter(k => k.kode !== kode);
            saveState(state);
        },

        // QA Simulation
        getQASimulation: function() {
            const state = loadState();
            return state.qaSimulation || { cloudDown: false, bugUpdate: false };
        },
        toggleCloudDown: function() {
            const state = loadState();
            if (!state.qaSimulation) state.qaSimulation = { cloudDown: false, bugUpdate: false };
            state.qaSimulation.cloudDown = !state.qaSimulation.cloudDown;
            const msg = state.qaSimulation.cloudDown
                ? '[SERVER] Cloud Down - seluruh layanan tidak dapat diakses'
                : '[SERVER] Cloud pulih - layanan normal kembali';
            state.eventLog.push({
                id: Date.now(),
                waktu: formatTime(Date.now()),
                kategori: state.qaSimulation.cloudDown ? 'Exception' : 'Info',
                deskripsi: msg,
                instansi: 'Pusat',
                eskalasi: false
            });
            saveState(state);
            return state.qaSimulation.cloudDown;
        },
        toggleBugUpdate: function() {
            const state = loadState();
            if (!state.qaSimulation) state.qaSimulation = { cloudDown: false, bugUpdate: false };
            state.qaSimulation.bugUpdate = !state.qaSimulation.bugUpdate;
            const msg = state.qaSimulation.bugUpdate
                ? '[AI] Bug Update - deteksi gestur error'
                : '[AI] Bug Update - telah di-rollback';
            state.eventLog.push({
                id: Date.now(),
                waktu: formatTime(Date.now()),
                kategori: state.qaSimulation.bugUpdate ? 'Exception' : 'Info',
                deskripsi: msg,
                instansi: 'Pusat',
                eskalasi: false
            });
            saveState(state);
            return state.qaSimulation.bugUpdate;
        },

        // Notifikasi
        getNotifCount: function() {
            const state = loadState();
            return state.insiden.filter(i => i.status === 'Baru' || i.status === 'Menunggu Approval').length;
        },

        // Proses Bantuan
        processBantuan: function(data) {
            const isError = (data.kategori === 'Kamera Error' || data.kategori === 'Suara Tidak Muncul' || data.kategori === 'Lainnya');
            if (isError) {
                const inc = this.addInsiden({
                    judul: data.deskripsi.substring(0, 45) + (data.deskripsi.length > 45 ? '...' : ''),
                    prioritas: 'Sedang',
                    instansi: data.instansi,
                    sumber: 'Laporan Web'
                });
                this.addEvent({
                    kategori: 'Exception',
                    deskripsi: '[WEB] ' + data.deskripsi.substring(0, 60),
                    instansi: data.instansi
                });
                return inc;
            } else {
                const req = this.addRequest({
                    jenis: 'Saran: ' + data.deskripsi.substring(0, 30),
                    prioritas: 'Rendah',
                    instansi: data.instansi,
                    sumber: 'Laporan Web'
                });
                return req;
            }
        }
    };

    global.StateManager = StateManager;

})(window);
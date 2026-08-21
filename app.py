import streamlit as st
import sqlite3
import pandas as pd

from services.auction_maintenance import close_empty_auctions
from services.budget_utils import budget_disponibile
from services.auction_utils import (
    get_leader,
    get_leader_name,
    count_active_participants
)
from services.auction_finalizer import (
    finalize_auction
)
from services.market_phase import get_market_phase
from services.market_status import get_market_phase
from services.market_automation import (
    close_single_participant_auctions,
    process_open_auctions
)
from services.sealed_bid_utils import analyze_sealed_bids
from services.round_utils import get_current_round
from services.audit_utils import log_event


# --------------------------------------------------
# CONFIGURAZIONE APP
# --------------------------------------------------

st.set_page_config(
    page_title="Fanta Bomberoni Market",
    layout="wide"
)

DB_PATH = r"database/fantalega.db"

VALUTA = "FM"
MODALITA_TEST = True


# --------------------------------------------------
# SESSIONE UTENTE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# --------------------------------------------------
# CONNESSIONE DB
# --------------------------------------------------

conn = sqlite3.connect(DB_PATH)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

if not st.session_state.logged_in:

    st.title("⚽ Fanta Bomberoni Market")

    utenti = pd.read_sql(
        """
        SELECT nome_account
        FROM users
        WHERE attivo = 1
        ORDER BY nome_account
        """,
        conn
    )

    account = st.selectbox(
        "Seleziona utente",
        utenti["nome_account"].tolist()
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Accedi"):

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                team_id,
                is_admin
            FROM users
            WHERE nome_account = ?
              AND password = ?
              AND attivo = 1
            """,
            (
                account,
                password
            )
        )

        utente = cursor.fetchone()

        if utente:

            st.session_state.logged_in = True

            st.session_state.current_user = account
            st.session_state.current_team_id = utente[1]
            st.session_state.is_admin = bool(
                utente[2]
            )

            st.rerun()

        else:

            st.error(
                "Password non corretta"
            )

    st.stop()


# --------------------------------------------------
# UTENTE AUTENTICATO
# --------------------------------------------------

CURRENT_USER = st.session_state.current_user
CURRENT_TEAM_ID = st.session_state.current_team_id
IS_ADMIN = st.session_state.is_admin
from services.time_utils import now_rome

st.warning(
    f"Ora sistema: {now_rome().strftime('%d/%m/%Y %H:%M:%S')}"
)

# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

if st.sidebar.button("🚪 Logout"):

    st.session_state.clear()
    st.rerun()


# --------------------------------------------------
# INTESTAZIONE SIDEBAR
# --------------------------------------------------

if CURRENT_USER == "ADMIN":
    send_telegram_message("🚀 Test da Streamlit")
    st.sidebar.success("👑 ADMIN")

else:

    st.sidebar.warning(
        f"🧪 {CURRENT_USER}"
    )



# --------------------------------------------------
# MERCATO
# --------------------------------------------------

FASE_MERCATO = get_market_phase()
if FASE_MERCATO == "BUSTE":

    close_single_participant_auctions()

elif FASE_MERCATO == "APERTURA_BUSTE":

    process_open_auctions()

descrizioni_fase = {
    "CHIAMATA": "🟢 Chiamate e rilanci",
    "RILANCIO": "🟡 Solo rilanci",
    "BUSTE": "🔵 Inserimento buste chiuse",
    "APERTURA_BUSTE": "🟣 Elaborazione buste",
    "CHIUSO": "🔴 Mercato chiuso"
}

st.info(
    f"Fase mercato: {descrizioni_fase[FASE_MERCATO]}"
)

if MODALITA_TEST:

    close_empty_auctions()

    st.warning(
        "⚠️ Modalità TEST attiva"
    )


# --------------------------------------------------
# MENU
# --------------------------------------------------

voci_menu = [
    "📊 Overview",
    "💰 Mercato",
    "↳ 📜 Archivio Mercato"
]

if IS_ADMIN:

    voci_menu.extend([
        "📜 Audit Log",
        "🛠️ Console Admin"
    ])

sezione = st.sidebar.radio(
    "Navigazione",
    voci_menu
)

if sezione == "📊 Overview":

    st.header("📊 Overview")

    query = """
    SELECT
        t.nome_squadra AS Squadra,
        t.cambi_residui AS Cambi,
        (500 - t.budget_residuo) AS Speso,
        t.budget_residuo AS Residuo,
        COUNT(r.player_id) AS Rosa
    FROM teams t
    LEFT JOIN rosters r
        ON t.team_id = r.team_id
    GROUP BY t.team_id
    ORDER BY t.nome_squadra
    """

    df = pd.read_sql(query, conn)
    df["Disponibile FM"] = df["Squadra"].apply(
        budget_disponibile
    )   
    df = df[
        [
            "Squadra",
            "Cambi",
            "Speso",
            "Residuo",
            "Disponibile FM",
            "Rosa"
        ]
    ]

    st.subheader("Cambi residui & Saldo")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("📜 Recap Mercato")

    query_recap = """
    SELECT
        p.player_id,
        p.nome AS Giocatore,
        p.ruolo AS Ruolo,
        mr.team_id_vincitore,
        mr.prezzo_acquisto,
        t.nome_squadra AS Vincitore,
        mr.player_id_ceduto,
        pc.nome AS Giocatore_Ceduto,
        mr.result_id
    FROM market_results mr

    JOIN players p
        ON mr.player_id_acquistato = p.player_id

    JOIN teams t
        ON mr.team_id_vincitore = t.team_id

    LEFT JOIN players pc
        ON mr.player_id_ceduto = pc.player_id
    
    WHERE mr.session_id = (
    SELECT session_id
    FROM market_sessions
    WHERE stato = 'APERTA'
    LIMIT 1
)

    ORDER BY mr.data_aggiudicazione DESC
    """

    df_recap = pd.read_sql(
        query_recap,
        conn
    )

    if len(df_recap) == 0:

        st.info(
            "Nessuna aggiudicazione registrata"
        )

    else:

        my_team_id = CURRENT_TEAM_ID

        righe_recap = []

        for _, riga in df_recap.iterrows():

            prezzo = f"{riga['prezzo_acquisto']:.2f} FM"

            # ------------------
            # CESSIONE GIA' SCELTA
            # ------------------

            if pd.notna(riga["Giocatore_Ceduto"]):

                ceduto = riga["Giocatore_Ceduto"]

            # ------------------
            # SONO IL VINCITORE
            # ------------------

            elif riga["team_id_vincitore"] == my_team_id:

                ruolo = riga["Ruolo"]

                giocatori_cedibili = pd.read_sql(
                    """
                    SELECT
                        p.player_id,
                        p.nome
                    FROM rosters r
                    JOIN players p
                        ON r.player_id = p.player_id
                    WHERE r.team_id = ?
                    AND r.attivo = 1
                    AND p.ruolo = ?
                    ORDER BY p.nome
                    """,
                    conn,
                    params=(
                        my_team_id,
                        ruolo
                    )
                )

                opzioni = {
                    row["nome"]: row["player_id"]
                    for _, row in giocatori_cedibili.iterrows()
                }

                scelta = st.selectbox(
                    f"Cessione per {riga['Giocatore']}",
                    ["-- Seleziona --"] + list(opzioni.keys()),
                    key=f"cessione_{riga['result_id']}"
                )

                if scelta != "-- Seleziona --":

                    player_id_ceduto = opzioni[scelta]

                    cursor = conn.cursor()

                    cursor.execute("""
                    UPDATE market_results
                    SET player_id_ceduto = ?
                    WHERE result_id = ?
                    """, (
                        player_id_ceduto,
                        riga["result_id"]
                    ))

                    conn.commit()

                    log_event(
                        conn,
                        CURRENT_USER,
                        "CESSIONE",
                        f"{riga['Giocatore']} → {scelta}"
                    )

                    st.rerun()

                ceduto = "⚠ Attesa cessione"

            # ------------------
            # ALTRI UTENTI
            # ------------------

            else:

                ceduto = "⚠ Attesa cessione"

            righe_recap.append({
                "Giocatore": riga["Giocatore"],
                "Ruolo": riga["Ruolo"],
                "Prezzo": prezzo,
                "Vincitore": riga["Vincitore"],
                "Giocatore ceduto": ceduto
            })

        st.dataframe(
            pd.DataFrame(righe_recap),
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Mercato in corso")

    query_aste = """
    SELECT
        a.auction_id,
        
        p.nome AS Giocatore,

        (
            SELECT MAX(pb.importo)
            FROM public_bids pb
            WHERE pb.auction_id = a.auction_id
        ) AS Offerta_Attuale,

        (
            SELECT t2.nome_squadra
            FROM public_bids pb2
            JOIN teams t2
                ON pb2.team_id = t2.team_id
            WHERE pb2.auction_id = a.auction_id
            ORDER BY pb2.importo DESC,
                    pb2.bid_id DESC
            LIMIT 1
        ) AS Leader,

        (
            SELECT COUNT(DISTINCT ap.team_id)
            FROM auction_participants ap
            WHERE ap.auction_id = a.auction_id
            AND ap.ha_abbandonato = 0
        ) AS Partecipanti

    FROM auctions a
    JOIN players p
        ON a.player_id = p.player_id

    WHERE a.stato = 'APERTA'

    ORDER BY a.auction_id DESC
    """


    aste = pd.read_sql(query_aste, conn)
    aste["Leader"] = aste["auction_id"].apply(
        get_leader_name
    )

    aste["Partecipanti"] = aste["auction_id"].apply(
        count_active_participants
    )
    aste = aste[
        [
            "Giocatore",
            "Offerta_Attuale",
            "Leader",
            "Partecipanti"
        ]
    ]
    if len(aste) == 0:
        st.info("Nessuna asta aperta")
    else:
        st.dataframe(
            aste,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("🏆 Premi")

    squadre = pd.read_sql(
        """
        SELECT
            team_id,
            nome_squadra
        FROM teams
        ORDER BY nome_squadra
        """,
        conn
    )

    mappa_squadre = {
        row["nome_squadra"]: row["team_id"]
        for _, row in squadre.iterrows()
    }

    query_premi = """
    SELECT
        p.prize_id,
        p.competizione,
        p.ranking,
        p.premio,
        t.nome_squadra
    FROM prizes p
    LEFT JOIN teams t
        ON p.team_id = t.team_id
    ORDER BY
        p.competizione,
        p.ranking
    """

    df_premi = pd.read_sql(
        query_premi,
        conn
    )

    df_premi.columns = [
        "prize_id",
        "Competizione",
        "Ranking",
        "Premio (€)",
        "Squadra"
    ]

    serie_a = df_premi[
        df_premi["Competizione"] == "Serie A"
    ]

    altri_premi = df_premi[
        df_premi["Competizione"] != "Serie A"
    ]
    st.markdown("### 🏆 Classifica Serie A")

    medaglie = {
        1: "🥇 1°",
        2: "🥈 2°",
        3: "🥉 3°"
    }

    for _, premio in serie_a.iterrows():

        col1, col2, col3, col4 = st.columns([1, 1, 3, 5])

        with col1:

            st.write(
                medaglie.get(
                    premio["Ranking"],
                    premio["Ranking"]
                )
            )

        with col2:

            st.markdown(
                f"<div style='text-align:right'>€ {premio['Premio (€)']:,.0f}</div>",
                unsafe_allow_html=True
            )

        with col3:

            if IS_ADMIN:

                squadra_attuale = (
                    premio["Squadra"]
                    if pd.notna(premio["Squadra"])
                    else "-- Seleziona --"
                )

                opzioni = (
                    ["-- Seleziona --"]
                    + list(mappa_squadre.keys())
                )

                scelta = st.selectbox(
                    "",
                    opzioni,
                    index=(
                        opzioni.index(squadra_attuale)
                        if squadra_attuale in opzioni
                        else 0
                    ),
                    key=f"premio_{premio['prize_id']}"
                )

                if (
                    scelta != "-- Seleziona --"
                    and scelta != squadra_attuale
                ):
                    cursor = conn.cursor()

                    cursor.execute("""
                    UPDATE prizes
                    SET team_id = ?
                    WHERE prize_id = ?
                    """, (
                        mappa_squadre[scelta],
                        premio["prize_id"]
                    ))

                    conn.commit()

                    log_event(
                        conn,
                        CURRENT_USER,
                        "PREMIO_ASSEGNATO",
                        f"{premio['Competizione']} - {scelta}"
                    )

                    st.rerun()

            else:

                st.markdown(
                    f"<div style='text-align:center'>{premio['Squadra'] if pd.notna(premio['Squadra']) else '-'}</div>",
                    unsafe_allow_html=True
                )

    st.markdown("### 🏅 Coppe e Competizioni")

    for _, premio in altri_premi.iterrows():

        col1, col2, col3, col4 = st.columns([1, 1, 3, 5])

        with col1:

            st.write(
                premio["Competizione"]
            )

        with col2:

            st.markdown(
                f"<div style='text-align:right'>€ {premio['Premio (€)']:,.0f}</div>",
                unsafe_allow_html=True
            )

        with col3:

            if IS_ADMIN:

                squadra_attuale = (
                    premio["Squadra"]
                    if pd.notna(premio["Squadra"])
                    else "-- Seleziona --"
                )

                opzioni = (
                    ["-- Seleziona --"]
                    + list(mappa_squadre.keys())
                )

                scelta = st.selectbox(
                    "",
                    opzioni,
                    index=(
                        opzioni.index(squadra_attuale)
                        if squadra_attuale in opzioni
                        else 0
                    ),
                    key=f"coppa_{premio['prize_id']}"
                )

                if (
                    scelta != "-- Seleziona --"
                    and scelta != squadra_attuale
                ):

                    cursor = conn.cursor()
                    
                    cursor.execute("""
                    UPDATE prizes
                    SET team_id = ?
                    WHERE prize_id = ?
                    """, (
                        mappa_squadre[scelta],
                        premio["prize_id"]
                    ))

                    log_event(
                        conn,
                        CURRENT_USER,
                        "PREMIO_ASSEGNATO",
                        f"{premio['Competizione']} - {scelta}"
                    )

                    conn.commit()

                    st.rerun()

            else:

                st.markdown(
                    f"<div style='text-align:center'>{premio['Squadra'] if pd.notna(premio['Squadra']) else '-'}</div>",
                    unsafe_allow_html=True
                )
    
    totale = df_premi["Premio (€)"].sum()

    st.success(
        f"💰 Montepremi totale: € {totale:,.0f}"
    )
    st.subheader("Dettaglio partecipanti")

    for _, asta in pd.read_sql(query_aste, conn).iterrows():

        auction_id = asta["auction_id"]
        giocatore = asta["Giocatore"]

        leader = get_leader(auction_id)

        if leader:
            offerta_leader = f"{leader[1]:.2f} FM"
        else:
            offerta_leader = "-"

        partecipanti = count_active_participants(
            auction_id
        )

        with st.expander(
            f"📋 {giocatore} • Leader: {get_leader_name(auction_id)} • {offerta_leader} • {partecipanti} partecipanti"
        ):

            leader_team_id = None

            if leader:
                leader_team_id = leader[0]

            dettaglio = pd.read_sql(
                """
                SELECT
                    t.team_id,
                    t.nome_squadra,
                    ap.ha_abbandonato,
                    MAX(pb.importo) AS offerta_massima
                FROM auction_participants ap
                JOIN teams t
                    ON ap.team_id = t.team_id
                LEFT JOIN public_bids pb
                    ON ap.auction_id = pb.auction_id
                AND ap.team_id = pb.team_id
                WHERE ap.auction_id = ?
                GROUP BY
                    t.team_id,
                    t.nome_squadra,
                    ap.ha_abbandonato
                ORDER BY offerta_massima DESC
                """,
                conn,
                params=(auction_id,)
            )

            righe = []

            for _, riga in dettaglio.iterrows():

                team_id = riga["team_id"]

                if riga["ha_abbandonato"] == 1:

                    stato = "🔴"

                elif team_id == leader_team_id:

                    stato = "🟢"

                else:

                    stato = "🟡"

                righe.append({
                    "Stato": stato,
                    "Squadra": riga["nome_squadra"],
                    "Offerta": (
                        f"{riga['offerta_massima']:.2f} FM"
                        if pd.notna(riga["offerta_massima"])
                        else "-"
                    )
                })

            for riga in righe:

                if riga["Stato"] == "🟢":

                    st.success(
                        f"🏆 {riga['Squadra']} (Leader) • {riga['Offerta']}"
                    )

                else:

                    col1, col2, col3 = st.columns([1, 6, 2])

                    with col1:

                        if riga["Stato"] == "🟡":
                            st.write("⏳")
                        else:
                            st.write("❌")

                    with col2:

                        if riga["Stato"] == "🔴":

                            st.markdown(
                                f"*{riga['Squadra']} (Abbandonato)*"
                            )

                        else:

                            st.markdown(
                                f"*{riga['Squadra']}*"
                            )

                    with col3:

                        st.write(
                            f"**{riga['Offerta']}**"
                        )

elif sezione == "💰 Mercato":

    st.header("💰 Mercato")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Chiamata",
        "Rilancio",
        "Abbandona",
        "Buste Chiuse"
    ])

    with tab1:

        st.subheader("Apri una nuova asta")

        conn = sqlite3.connect(DB_PATH)

        if IS_ADMIN:

            st.warning(
                "L'amministratore non può partecipare alle aste"
            )

            st.stop()

        st.info(
            f"Squadra attiva: {CURRENT_USER}"
        )

        svincolati = pd.read_sql(
            """
            SELECT
                p.player_id,
                p.nome,
                p.ruolo,
                p.squadra_serie_a
            FROM players p
            LEFT JOIN rosters r
                ON p.player_id = r.player_id
            WHERE r.player_id IS NULL
            ORDER BY p.nome
            """,
            conn
        )

        svincolati["label"] = (
            svincolati["nome"]
            + " ("
            + svincolati["ruolo"]
            + " - "
            + svincolati["squadra_serie_a"]
            + ")"
        )

        giocatore = st.selectbox(
            "Giocatore",
            svincolati["label"]
        )

        offerta = st.number_input(
            "Offerta iniziale",
            min_value=0.50,
            step=0.50,
            value=0.50
        )

        if IS_ADMIN:

            st.write(
                "Budget disponibile: Amministratore"
            )

        else:

            budget_attuale = budget_disponibile(
                CURRENT_USER
            )

            st.write(
                f"Budget disponibile: {budget_attuale:.2f} FM"
            )

        if FASE_MERCATO != "CHIAMATA":

            st.error(
                "Nuove aste non consentite in questa fase."
            )

        else:
            if st.button("Apri Asta"):

                if offerta > budget_attuale:

                    st.error(
                        "Budget insufficiente"
                    )

                else:
                
                    player_id = int(
                        svincolati.loc[
                            svincolati["label"] == giocatore,
                            "player_id"
                        ].iloc[0]
                    )

                    team_id = CURRENT_TEAM_ID

                    cursor = conn.cursor()

                    cursor.execute("""
                    SELECT COUNT(*)
                    FROM auctions
                    WHERE player_id = ?
                    AND stato = 'APERTA'
                    """, (player_id,))

                    asta_esistente = cursor.fetchone()[0]

                    if asta_esistente > 0:

                        st.error(
                            "Esiste già un'asta aperta per questo giocatore."
                        )

                    else:

                        cursor.execute("""
                        INSERT INTO auctions (
                            session_id,
                            player_id,
                            team_chiamante,
                            prezzo_partenza,
                            data_apertura,
                            stato
                        )
                        VALUES (
                            1,
                            ?,
                            ?,
                            ?,
                            datetime('now'),
                            'APERTA'
                        )
                        """, (
                            player_id,
                            team_id,
                            offerta
                        ))

                        auction_id = cursor.lastrowid

                        from services.telegram_utils import send_telegram_message

                        send_telegram_message(
                            f"""📢 NUOVA ASTA

                        Player ID: {player_id}
                        Team ID: {team_id}
                        Base: {offerta:.2f} FM
                        """
                        )
                                
                        cursor.execute("""
                        INSERT INTO public_bids (
                            auction_id,
                            team_id,
                            importo,
                            data_ora
                        )
                        VALUES (
                            ?,
                            ?,
                            ?,
                            datetime('now')
                        )
                        """, (
                            auction_id,
                            team_id,
                            offerta
                        ))

                        cursor.execute("""
                        INSERT INTO auction_participants (
                            auction_id,
                            team_id,
                            ha_abbandonato
                        )
                        VALUES (?, ?, 0)
                        """, (
                            auction_id,
                            team_id
                        ))
                        conn.commit()

                        log_event(
                            conn,
                            CURRENT_USER,
                            "APERTURA_ASTA",
                            giocatore
                        )

                        st.success("Asta creata correttamente")

        conn.close()

    with tab2:

        st.subheader("Rilancio")

        conn = sqlite3.connect(DB_PATH)

        if IS_ADMIN:

            st.warning(
                "L'amministratore non può partecipare alle aste"
            )

        else:

            aste = pd.read_sql(
                """
                SELECT
                    a.auction_id,
                    p.nome
                FROM auctions a
                JOIN players p
                    ON a.player_id = p.player_id
                WHERE a.stato = 'APERTA'
                ORDER BY p.nome
                """,
                conn
            )

            if len(aste) == 0:

                st.info("Nessuna asta aperta")

            else:

                aste["label"] = (
                    aste["auction_id"].astype(str)
                    + " - "
                    + aste["nome"]
                )

                asta_selezionata = st.selectbox(
                    "Asta",
                    aste["label"],
                    key="rilancio_asta"
                )

                auction_id = int(
                    aste.loc[
                        aste["label"] == asta_selezionata,
                        "auction_id"
                    ].iloc[0]
                )

                nome_giocatore = aste.loc[
                    aste["label"] == asta_selezionata,
                    "nome"
                ].iloc[0]

                team_id = CURRENT_TEAM_ID

                cursor = conn.cursor()

                cursor.execute("""
                SELECT ha_abbandonato
                FROM auction_participants
                WHERE auction_id = ?
                AND team_id = ?
                """, (
                    auction_id,
                    team_id
                ))

                risultato = cursor.fetchone()

                ha_abbandonato = False

                if risultato:
                    ha_abbandonato = bool(risultato[0])

                if ha_abbandonato:

                    st.error(
                        "Hai abbandonato questa asta. Non puoi più effettuare rilanci."
                    )

                else:

                    ultima_offerta = pd.read_sql(
                        f"""
                        SELECT MAX(importo) AS max_offerta
                        FROM public_bids
                        WHERE auction_id = {auction_id}
                        """,
                        conn
                    )

                    max_offerta = float(
                        ultima_offerta.iloc[0]["max_offerta"]
                    )

                    st.write(
                        f"Offerta attuale: € {max_offerta:.2f}"
                    )

                    nuova_offerta = st.number_input(
                        "Nuova offerta",
                        min_value=0.50,
                        value=max_offerta + 0.50,
                        step=0.50
                    )

                    budget_attuale = budget_disponibile(
                        CURRENT_USER
                    )

                    st.write(
                        f"Budget disponibile: {budget_attuale:.2f} FM"
                    )

                    if FASE_MERCATO not in [
                        "CHIAMATA",
                        "RILANCIO"
                    ]:

                        st.error(
                            "I rilanci pubblici non sono consentiti in questa fase."
                        )

                    else:

                        if st.button("Rilancia"):

                            if nuova_offerta < (max_offerta + 0.50):

                                st.error(
                                    f"Offerta non valida. Minimo consentito: {max_offerta + 0.50:.2f} FM"
                                )

                            elif nuova_offerta > budget_attuale:

                                st.error(
                                    "Budget insufficiente"
                                )

                            else:

                                cursor.execute("""
                                INSERT INTO public_bids (
                                    auction_id,
                                    team_id,
                                    importo,
                                    data_ora
                                )
                                VALUES (
                                    ?,
                                    ?,
                                    ?,
                                    datetime('now')
                                )
                                """, (
                                    auction_id,
                                    team_id,
                                    nuova_offerta
                                ))

                                cursor.execute("""
                                SELECT COUNT(*)
                                FROM auction_participants
                                WHERE auction_id = ?
                                AND team_id = ?
                                """, (
                                    auction_id,
                                    team_id
                                ))

                                esiste = cursor.fetchone()[0]

                                if esiste == 0:

                                    cursor.execute("""
                                    INSERT INTO auction_participants (
                                        auction_id,
                                        team_id,
                                        ha_abbandonato
                                    )
                                    VALUES (
                                        ?,
                                        ?,
                                        0
                                    )
                                    """, (
                                        auction_id,
                                        team_id
                                    ))

                                conn.commit()

                                log_event(
                                    conn,
                                    CURRENT_USER,
                                    "RILANCIO",
                                    f"{nome_giocatore} - {nuova_offerta:.2f} FM"
                                )

                                st.success(
                                    "Rilancio registrato"
                                )

        conn.close()

    with tab3:

        st.subheader("Abbandona asta")

        if FASE_MERCATO not in [
            "CHIAMATA",
            "RILANCIO",
            "BUSTE"
        ]:

            st.error(
                "Non è possibile abbandonare aste in questa fase."
            )

        else:

            conn = sqlite3.connect(DB_PATH)

            cursor = conn.cursor()

            # Recupero ID squadra loggata
            
            team_id = CURRENT_TEAM_ID

            aste = pd.read_sql(
                f"""
                SELECT DISTINCT
                    a.auction_id,
                    p.nome
                FROM auction_participants ap
                JOIN auctions a
                    ON ap.auction_id = a.auction_id
                JOIN players p
                    ON a.player_id = p.player_id
                WHERE ap.team_id = {team_id}
                AND ap.ha_abbandonato = 0
                AND a.stato = 'APERTA'
                ORDER BY p.nome
                """,
                conn
            )

            if len(aste) == 0:

                st.info("Nessuna asta disponibile")

            else:

                aste["label"] = (
                    aste["auction_id"].astype(str)
                    + " - "
                    + aste["nome"]
                )

                asta_selezionata = st.selectbox(
                    "Asta",
                    aste["label"],
                    key="abbandono_asta"
                )

                if st.button("Abbandona definitivamente"):

                    auction_id = int(
                        aste.loc[
                            aste["label"] == asta_selezionata,
                            "auction_id"
                        ].iloc[0]
                    )

                    nome_giocatore = aste.loc[
                        aste["label"] == asta_selezionata,
                        "nome"
                    ].iloc[0]
                                        
                    leader = get_leader(auction_id)

                    if (
                        leader
                        and leader[0] == team_id
                    ):

                        st.error(
                            "Impossibile abbandonare. Sei il miglior offerente attuale."
                        )

                    else:
                    
                        cursor.execute("""
                        UPDATE auction_participants
                        SET ha_abbandonato = 1
                        WHERE auction_id = ?
                        AND team_id = ?
                        """, (
                            auction_id,
                            team_id
                        ))

                        conn.commit()

                        log_event(
                            conn,
                            CURRENT_USER,
                            "ABBANDONO",
                            nome_giocatore
                        )

                        st.success(
                            "Abbandono registrato"
                        )

        conn.close()

    with tab4:

        st.subheader("Buste Chiuse")

        if FASE_MERCATO != "BUSTE":

            st.warning(
                "L'inserimento delle buste è consentito solo dalle 12:00 alle 16:59 del venerdì."
            )

        else:

            # tutto il codice esistente

            conn = sqlite3.connect(DB_PATH)

            cursor = conn.cursor()

            query = """
            SELECT
                a.auction_id,
                p.nome AS Giocatore
            FROM auctions a
            JOIN players p
                ON a.player_id = p.player_id
            WHERE a.stato = 'APERTA'
            """

            aste = pd.read_sql(query, conn)

            if len(aste) == 0:

                st.info(
                    "Nessuna asta aperta"
                )

            else:

                aste["Partecipanti"] = aste["auction_id"].apply(
                    count_active_participants
                )

                aste_busta = aste[
                    aste["Partecipanti"] > 1
                ].copy()

                team_id = CURRENT_TEAM_ID

                aste_valide = []

                for auction_id in aste_busta["auction_id"]:

                    round_corrente = get_current_round(
                        auction_id
                    )

                    # Nessuno spareggio attivo
                    if round_corrente is None:

                        cursor.execute("""
                        SELECT COUNT(*)
                        FROM auction_participants
                        WHERE auction_id = ?
                        AND team_id = ?
                        AND ha_abbandonato = 0
                        """, (
                            auction_id,
                            team_id
                        ))

                        partecipa = cursor.fetchone()[0]

                    else:

                        round_id = round_corrente[0]

                        cursor.execute("""
                        SELECT COUNT(*)
                        FROM round_participants
                        WHERE round_id = ?
                        AND team_id = ?
                        """, (
                            round_id,
                            team_id
                        ))

                        partecipa = cursor.fetchone()[0]

                    if partecipa > 0:

                        aste_valide.append(auction_id)

                aste_busta = aste_busta[
                    aste_busta["auction_id"].isin(
                        aste_valide
                    )
                ]

                if len(aste_busta) == 0:

                    st.info(
                        "Nessuna asta necessita delle buste chiuse"
                    )

                else:

                    offerte_attuali = []
                    offerte_minime = []

                    for auction_id in aste_busta["auction_id"]:

                        leader = get_leader(auction_id)

                        if leader:
                            offerte_attuali.append(leader[1])
                        else:
                            offerte_attuali.append(0)

                        round_corrente = get_current_round(
                            auction_id
                        )

                        if round_corrente is None:

                            if leader:
                                offerte_minime.append(
                                    leader[1] + 0.50
                                )
                            else:
                                offerte_minime.append(
                                    0.50
                                )

                        else:

                            cursor.execute("""
                            SELECT offerta_minima
                            FROM sealed_rounds
                            WHERE round_id = ?
                            """, (
                                round_corrente[0],
                            ))

                            offerta_minima_round = cursor.fetchone()[0]

                            offerte_minime.append(
                                offerta_minima_round
                            )

                    aste_busta["Offerta_Attuale"] = offerte_attuali

                    aste_busta["Leader"] = aste_busta["auction_id"].apply(
                        get_leader_name
                    )

                    aste_busta["Offerta Minima"] = offerte_minime

                    st.dataframe(
                        aste_busta[
                            [
                                "Giocatore",
                                "Offerta_Attuale",
                                "Offerta Minima",
                                "Leader",
                                "Partecipanti"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.divider()

                    aste_busta["label"] = (
                        aste_busta["Giocatore"]
                        + " | Min: "
                        + aste_busta["Offerta Minima"].astype(str)
                        + " FM"
                    )

                    asta_selezionata = st.selectbox(
                        "Asta",
                        aste_busta["label"],
                        key="busta_asta"
                    )

                    auction_id = int(
                        aste_busta.loc[
                            aste_busta["label"] == asta_selezionata,
                            "auction_id"
                        ].iloc[0]
                    )

                    offerta_minima = float(
                        aste_busta.loc[
                            aste_busta["label"] == asta_selezionata,
                            "Offerta Minima"
                        ].iloc[0]
                    )

                    st.write(
                        f"Offerta minima ammessa: {offerta_minima:.2f} FM"
                    )

                    offerta_busta = st.number_input(
                        "Offerta segreta",
                        min_value=0.50,
                        value=offerta_minima,
                        step=0.50,
                        key="offerta_busta"
                    )

                    if st.button(
                        "Invia Busta",
                        key="invia_busta"
                    ):
                        if offerta_busta < offerta_minima:

                            st.error(
                                f"Offerta non valida. Minimo consentito: {offerta_minima:.2f} FM"
                            )

                        else:
                            team_id = CURRENT_TEAM_ID

                            # Verifica se esiste uno spareggio aperto
                            round_corrente = get_current_round(
                                auction_id
                            )

                            # --------------------------
                            # ROUND 1
                            # --------------------------

                            if round_corrente is None:

                                round_id = 0
                                round_number = 1

                                cursor.execute("""
                                SELECT COUNT(*)
                                FROM auction_participants
                                WHERE auction_id = ?
                                AND team_id = ?
                                AND ha_abbandonato = 0
                                """, (
                                    auction_id,
                                    team_id
                                ))

                                abilitato = cursor.fetchone()[0]

                            # --------------------------
                            # ROUND 2+
                            # --------------------------

                            else:

                                round_id = round_corrente[0]
                                round_number = round_corrente[1]

                                cursor.execute("""
                                SELECT COUNT(*)
                                FROM round_participants
                                WHERE round_id = ?
                                AND team_id = ?
                                """, (
                                    round_id,
                                    team_id
                                ))

                                abilitato = cursor.fetchone()[0]

                            # --------------------------
                            # Utente non ammesso
                            # --------------------------

                            if abilitato == 0:

                                st.error(
                                    "Non hai diritto a partecipare a questo round."
                                )

                            else:

                                # Una sola busta per team
                                cursor.execute("""
                                DELETE FROM sealed_bids
                                WHERE round_id = ?
                                AND auction_id = ?
                                AND team_id = ?
                                """, (
                                    round_id,
                                    auction_id,
                                    team_id
                                ))

                                cursor.execute("""
                                INSERT INTO sealed_bids (
                                    round_id,
                                    auction_id,
                                    team_id,
                                    importo,
                                    data_ora
                                )
                                VALUES (
                                    ?,
                                    ?,
                                    ?,
                                    ?,
                                    datetime('now')
                                )
                                """, (
                                    round_id,
                                    auction_id,
                                    team_id,
                                    offerta_busta
                                ))

                                conn.commit()

                                log_event(
                                    conn,
                                    CURRENT_USER,
                                    "BUSTA",
                                    f"{nome_giocatore} - {offerta_busta:.2f} FM"
                                )

                                st.success(
                                    f"Busta registrata correttamente (Round {round_number})"
                                )
                            
                    st.divider()

                    st.subheader("Apertura Buste (TEST)")

                    aste_apribili = aste_busta.copy()

                    if len(aste_apribili) > 0:

                        aste_apribili["label"] = (
                            aste_apribili["Giocatore"]
                        )

                        asta_apertura = st.selectbox(
                            "Seleziona asta da aprire",
                            aste_apribili["label"],
                            key="apertura_buste"
                        )

                        auction_id_apertura = int(
                            aste_apribili.loc[
                                aste_apribili["label"] == asta_apertura,
                                "auction_id"
                            ].iloc[0]
                        )

                        if st.button(
                            "Apri Buste",
                            key="apri_buste"
                        ):

                            buste = pd.read_sql(
                                f"""
                                SELECT
                                    t.nome_squadra AS Squadra,
                                    sb.importo AS Offerta
                                FROM sealed_bids sb
                                JOIN teams t
                                    ON sb.team_id = t.team_id
                                WHERE sb.auction_id = {auction_id_apertura}
                                ORDER BY sb.importo DESC
                                """,
                                conn
                            )

                            st.subheader("Risultato Buste")

                            st.dataframe(
                                buste,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            risultato = analyze_sealed_bids(
                                auction_id_apertura
                            )

                            if risultato["tipo"] == "LEADER_PUBBLICO":

                                finalize_auction(
                                    conn,
                                    auction_id_apertura,
                                    risultato
                                )

                                cursor.execute("""
                                SELECT nome_squadra
                                FROM teams
                                WHERE team_id = ?
                                """, (
                                    risultato["team_id"],
                                ))

                                nome_squadra = cursor.fetchone()[0]

                                st.success(
                                    f"Vince il leader pubblico: {nome_squadra} ({risultato['offerta']:.2f} FM)"
                                )

                            elif risultato["tipo"] == "VINCITORE":

                                finalize_auction(
                                    conn,
                                    auction_id_apertura,
                                    risultato
                                )

                                cursor.execute("""
                                SELECT nome_squadra
                                FROM teams
                                WHERE team_id = ?
                                """, (
                                    risultato["team_id"],
                                ))

                                nome_squadra = cursor.fetchone()[0]

                                st.success(
                                    f"Vincitore: {nome_squadra} ({risultato['offerta']:.2f} FM)"
                                )

                            elif risultato["tipo"] == "PARITA":

                                st.error(
                                    f"Parità a {risultato['offerta']:.2f} FM - necessario spareggio"
                                )

                                cursor.execute("""
                                SELECT MAX(round_number)
                                FROM sealed_rounds
                                WHERE auction_id = ?
                                """, (
                                    auction_id_apertura,
                                ))

                                ultimo_round = cursor.fetchone()[0]

                                if ultimo_round is None:
                                    ultimo_round = 1

                                nuovo_round = ultimo_round + 1

                                cursor.execute("""
                                UPDATE sealed_rounds
                                SET stato = 'CHIUSO'
                                WHERE auction_id = ?
                                AND stato = 'APERTO'
                                """, (
                                    auction_id_apertura,
                                ))

                                cursor.execute("""
                                INSERT INTO sealed_rounds (
                                    auction_id,
                                    round_number,
                                    apertura,
                                    chiusura,
                                    stato,
                                    offerta_minima
                                )
                                VALUES (
                                    ?,
                                    ?,
                                    datetime('now'),
                                    datetime('now'),
                                    'APERTO',
                                    ?
                                )
                                """, (
                                    auction_id_apertura,
                                    nuovo_round,
                                    risultato["offerta"] + 0.50
                                ))

                                round_id = cursor.lastrowid

                                for team_id in risultato["team_ids"]:

                                    cursor.execute("""
                                    INSERT INTO round_participants (
                                        round_id,
                                        team_id
                                    )
                                    VALUES (?, ?)
                                    """, (
                                        round_id,
                                        team_id
                                    ))

                                conn.commit()

                                st.warning(
                                    f"Creato round di spareggio n. {nuovo_round}"
                                )

                                st.info(
                                    f"Nuova offerta minima: {risultato['offerta'] + 0.50:.2f} FM"
                                )
        conn.close()

elif sezione == "↳ 📜 Archivio Mercato":

    st.header("📜 Archivio Mercato")

    query_archivio = """
    SELECT
        p.nome AS Giocatore,
        p.ruolo AS Ruolo,
        mr.prezzo_acquisto,
        t.nome_squadra AS Vincitore,
        pc.nome AS Giocatore_Ceduto,
        mr.data_aggiudicazione,
        ms.descrizione AS Sessione
    FROM market_results mr

    JOIN players p
        ON mr.player_id_acquistato = p.player_id

    JOIN teams t
        ON mr.team_id_vincitore = t.team_id

    LEFT JOIN players pc
        ON mr.player_id_ceduto = pc.player_id

    LEFT JOIN market_sessions ms
        ON mr.session_id = ms.session_id

    ORDER BY mr.data_aggiudicazione DESC
    """

    df_archivio = pd.read_sql(
        query_archivio,
        conn
    )
    df_archivio["Data"] = pd.to_datetime(
        df_archivio["data_aggiudicazione"]
    ).dt.strftime("%d/%m/%Y")

    if len(df_archivio) == 0:

        st.info(
            "Nessuna operazione di mercato registrata"
        )

    else:

        df_archivio["Prezzo"] = (
            df_archivio["prezzo_acquisto"]
            .apply(lambda x: f"{x:.2f} FM")
        )

        df_archivio["Giocatore ceduto"] = (
            df_archivio["Giocatore_Ceduto"]
            .fillna("⚠ Attesa cessione")
        )

        st.dataframe(
            df_archivio[
                [
                    "Data",
                    "Sessione",
                    "Giocatore",
                    "Ruolo",
                    "Prezzo",
                    "Vincitore",
                    "Giocatore ceduto"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )
        
elif sezione == "📜 Audit Log":

    st.header("📜 Audit Log")

    query_log = """
    SELECT
        data_evento,
        squadra,
        tipo_evento,
        dettaglio
    FROM audit_log
    ORDER BY data_evento DESC
    """

    df_log = pd.read_sql(
        query_log,
        conn
    )
    
    if len(df_log) == 0:

        st.info(
            "Nessun evento registrato"
        )

    else:

        df_log["data_evento"] = (
            pd.to_datetime(df_log["data_evento"], utc=True)
            .dt.tz_convert("Europe/Rome")
            .dt.strftime("%d/%m/%Y %H:%M")
        )

        df_log = df_log.rename(
            columns={
                "data_evento": "Data",
                "squadra": "Utente",
                "tipo_evento": "Evento",
                "dettaglio": "Dettaglio"
            }
        )

        st.dataframe(
            df_log[
                [
                    "Data",
                    "Utente",
                    "Evento",
                    "Dettaglio"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

elif sezione == "🛠️ Console Admin":

    st.header("🛠️ Console Admin")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT setting_value
    FROM system_settings
    WHERE setting_key = 'MARKET_OVERRIDE'
    """)

    stato = cursor.fetchone()[0]

    st.subheader("⚙️ Stato Mercato")

    st.write(
        f"Modalità attuale: **{stato}**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("🟢 AUTO"):

            cursor.execute("""
            UPDATE system_settings
            SET setting_value = 'AUTO'
            WHERE setting_key = 'MARKET_OVERRIDE'
            """)

            conn.commit()

            log_event(
                conn,
                CURRENT_USER,
                "OVERRIDE_MERCATO",
                "AUTO"
            )

            st.rerun()

    with col2:

        if st.button("🔓 FORZA APERTO"):

            cursor.execute("""
            UPDATE system_settings
            SET setting_value = 'APERTO'
            WHERE setting_key = 'MARKET_OVERRIDE'
            """)

            conn.commit()

            log_event(
                conn,
                CURRENT_USER,
                "OVERRIDE_MERCATO",
                "APERTO"
            )

            st.rerun()

    with col3:

        if st.button("🔒 FORZA CHIUSO"):

            cursor.execute("""
            UPDATE system_settings
            SET setting_value = 'CHIUSO'
            WHERE setting_key = 'MARKET_OVERRIDE'
            """)

            conn.commit()

            log_event(
                conn,
                CURRENT_USER,
                "OVERRIDE_MERCATO",
                "CHIUSO"
            )

            st.rerun()
        st.divider()

        st.subheader("🧪 Forzatura Fase")

        cursor.execute("""
        SELECT setting_value
        FROM system_settings
        WHERE setting_key = 'MARKET_PHASE_OVERRIDE'
        """)

        fase_corrente = cursor.fetchone()[0]

        st.write(
            f"Fase forzata attuale: **{fase_corrente}**"
        )

        fase_test = st.selectbox(
            "Seleziona fase",
            [
                "AUTO",
                "CHIAMATA",
                "RILANCIO",
                "BUSTE",
                "APERTURA_BUSTE",
                "CHIUSO"
            ]
        )

        if st.button("✅ Applica Fase"):

            cursor.execute("""
            UPDATE system_settings
            SET setting_value = ?
            WHERE setting_key = 'MARKET_PHASE_OVERRIDE'
            """, (
                fase_test,
            ))

            conn.commit()

            log_event(
                conn,
                CURRENT_USER,
                "OVERRIDE_FASE",
                fase_test
            )

            st.rerun()

        st.divider()
    st.divider()

    st.subheader("🧪 Simulazione Utente")

    utenti_test = pd.read_sql(
        """
        SELECT
            nome_account,
            team_id,
            is_admin
        FROM users
        ORDER BY nome_account
        """,
        conn
    )

    utente_test = st.selectbox(
        "Impersona utente",
        utenti_test["nome_account"].tolist()
    )

    if st.button("🔄 Impersona"):

        riga = utenti_test[
            utenti_test["nome_account"] == utente_test
        ].iloc[0]

        st.session_state.current_user = riga["nome_account"]

        st.session_state.current_team_id = riga["team_id"]

        st.session_state.is_admin = bool(
            riga["is_admin"]
        )

        st.rerun()

    if st.button("👑 Torna ad ADMIN"):

        cursor.execute("""
        SELECT
            nome_account,
            team_id,
            is_admin
        FROM users
        WHERE nome_account = 'ADMIN'
        """)

        admin = cursor.fetchone()

        st.session_state.current_user = admin[0]

        st.session_state.current_team_id = admin[1]

        st.session_state.is_admin = bool(
            admin[2]
        )

        st.rerun()
conn.close()
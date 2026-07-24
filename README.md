# Janitza UMG 604-PRO voor Home Assistant

Lokale, alleen-lezen Home Assistant-integratie voor een Janitza UMG 604-PRO via Modbus TCP.

## Installatie

### Via HACS

Deze integratie kan via HACS als custom repository worden geïnstalleerd zodra deze map op GitHub staat.

1. Open **HACS** in Home Assistant.
2. Ga naar **Integraties**.
3. Kies rechtsboven **Custom repositories**.
4. Vul de GitHub repository-URL in.
5. Kies categorie **Integration**.
6. Download **Janitza UMG 604-PRO**.
7. Herstart Home Assistant.
8. Voeg de integratie toe via **Instellingen > Apparaten & diensten > Integratie toevoegen**.

Let op: vervang in `custom_components/janitza_umg604/manifest.json` eerst de placeholder
`REPLACE_WITH_GITHUB_OWNER` door jouw echte GitHub-gebruikersnaam of organisatie.

### Handmatig

1. Kopieer `custom_components/janitza_umg604` naar de map `config/custom_components/` van Home Assistant.
2. Herstart Home Assistant.
3. Ga naar **Instellingen > Apparaten & diensten > Integratie toevoegen**.
4. Zoek naar **Janitza UMG 604-PRO**.
5. Vul IP-adres, poort (standaard 502), unit-ID (vaak 1) en uitleesinterval in.

Laat de register-offset eerst op `0` staan. Gebruik alleen `-1` als jouw apparaat of firmware aantoonbaar één register verschoven antwoordt.

De integratie schrijft nooit naar Modbus-registers.

## Sensoren

De integratie levert nu dezelfde hoofdwaarden als het lokale webdashboard:

- fase- en lijnspanningen
- fasestromen
- actief vermogen per fase
- totaal actief, reactief en schijnbaar vermogen
- power factor totaal, per fase en gemiddeld
- frequentie
- afgenomen en teruggeleverde energie
- schijnbare energie en blindenergie
- temperatuur
- spannings- en stroomonbalans
- fasevolgorde
- cosinus phi per fase
- THD spanning en stroom per fase
- TDD stroom per fase
- digitale ingangen
- gebeurtenis-, flag- en transiënttellers
- serienummer, productienummer, apparaatnaam, omschrijving en firmware
- stroomtrafo- en spanningstrafo-instellingen per fase

De energietellers worden omgerekend van Wh naar kWh en zijn geschikt voor langdurige Home Assistant-statistieken.

## Lokaal webdashboard

In de map `dashboard` staat ook een zelfstandig, alleen-lezen webdashboard. Hiervoor is
alleen Python 3 nodig; extra Python-pakketten zijn niet vereist.

1. Dubbelklik op `dashboard/start_dashboard.bat`.
2. Open `http://127.0.0.1:8080` in een browser.
3. Vul het IP-adres, de Modbus-poort, unit-ID en register-offset in.
4. Klik op **Uitlezen**. Na een geslaagde meting wordt iedere 10 seconden vernieuwd.

De instellingen blijven alleen lokaal in de browser bewaard. De webserver luistert
uitsluitend op deze computer (`127.0.0.1`) en schrijft nooit naar de meter.

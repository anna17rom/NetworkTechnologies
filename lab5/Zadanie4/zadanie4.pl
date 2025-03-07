# Importujemy moduły potrzebne do stworzenia serwera HTTP i obsługi statusów HTTP
use HTTP::Daemon;
use HTTP::Status;
use File::Slurp;

# Tworzymy nową instancję serwera HTTP nasłuchującą na adresie lokalnym i porcie 4301
my $d = HTTP::Daemon->new(
           LocalAddr => 'localhost',
           LocalPort => 4301,
       ) || die "Cannot start server: $!";  # Zakończenie programu w przypadku błędu podczas uruchamiania serwera

# Wyświetlamy informację o adresie URL serwera
print "Server is running at: ", $d->url, "\n";

# Główna pętla obsługująca połączenia przychodzące
while (my $c = $d->accept) {  # Akceptujemy nowe połączenie
    while (my $r = $c->get_request) {  # Pobieramy żądanie HTTP od klienta
        if ($r->method eq 'GET') {  # Sprawdzamy, czy metoda żądania to GET
            # Ustawiamy domyślną stronę startową, jeśli dostępne jest tylko `/`
            my $file_path = "./www" . $r->url->path;  # Tworzymy ścieżkę do pliku na podstawie żądanego URL
            $file_path .= "first.html" if $file_path =~ /\/$/;  # Jeśli ścieżka kończy się na `/`, dodajemy `first.html`

            # Obsługa żądania pliku
            if (-e $file_path && -f $file_path) {  # Sprawdzamy, czy plik istnieje i jest zwykłym plikiem
                my $content = read_file($file_path);  # Odczytujemy zawartość pliku
                # Wysyłamy odpowiedź z kodem 200 (OK) oraz zawartością pliku
                $c->send_response(HTTP::Response->new(200, 'OK', ['Content-Type' => 'text/html; charset=utf-8'], $content));
            } else {
                $c->send_error(RC_NOT_FOUND);  # Wysyłamy odpowiedź z kodem 404 (Not Found), jeśli plik nie istnieje
            }
        } else {
            $c->send_error(RC_FORBIDDEN);  # Wysyłamy odpowiedź z kodem 403 (Forbidden) dla innych metod niż GET
        }
    }
    $c->close;  # Zamykamy połączenie
    undef($c);  # Usuwamy referencję do połączenia
}

# Funkcja do odczytywania plików
sub read_file {
    my $filename = shift;  # Pobieramy nazwę pliku jako argument funkcji
    open my $fh, '<:encoding(UTF-8)', $filename or die "Cannot open file: $!";  # Otwieramy plik do odczytu z kodowaniem UTF-8
    local $/ = undef;  # Ustawiamy specjalny separator, aby odczytać cały plik naraz
    my $content = <$fh>;  # Odczytujemy zawartość pliku
    close $fh;  # Zamykamy plik
    return $content;  # Zwracamy zawartość pliku
}



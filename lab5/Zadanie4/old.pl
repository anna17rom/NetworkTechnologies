use HTTP::Daemon;
use HTTP::Status;  

# Utworzenie obiektu daemon na lokalnym adresie i porcie
my $d = HTTP::Daemon->new(
           LocalAddr => 'localhost',  # Adres lokalny
           LocalPort => 4321,
       ) || die "Nie można uruchomić serwera: $!";

print "Please contact me at: <URL:", $d->url, ">\n";

# Ścieżka do katalogu z plikami HTML
my $www_dir = '/home/anna/mk1-272395/TS/lab5/www';

# Serwer obsługujący połączenia
while (my $c = $d->accept) {
    while (my $r = $c->get_request) {
        if ($r->method eq 'GET') {
            # Określenie żądanej ścieżki
            my $path = $r->url->path;
            # Ustawienie domyślnej strony na 'first.html' jeśli ścieżka to '/'
            $path = 'first.html' if $path eq '/';
            my $file_path = "$www_dir/$path";

            # Sprawdzenie, czy plik istnieje i jest plikiem regularnym
            if (-e $file_path && -f $file_path) {
                $c->send_file_response($file_path);
            } else {
                # Wysyłanie odpowiedzi 404 Not Found jeśli plik nie istnieje
                $c->send_error(RC_NOT_FOUND);
            }
        } else {
            # Obsługa innych metod niż GET przez wysłanie odpowiedzi 403 Forbidden
            $c->send_error(RC_FORBIDDEN);
        }
    }
    # Zamknięcie połączenia
    $c->close;
    undef($c);
}

